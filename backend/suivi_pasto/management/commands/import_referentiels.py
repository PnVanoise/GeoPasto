import json

from django.db import connection, transaction
from django.core.management.base import BaseCommand, CommandError
from auditlog.registry import auditlog as auditlog_registry


def _disable_auditlog():
    for model in list(auditlog_registry.get_models()):
        auditlog_registry.unregister(model)


from suivi_pasto.models import (
    CategorieAnimaux,
    CategoriePension,
    Commodite,
    Enjeu,
    Espece,
    Production,
    Race,
    TypeConvention,
    TypeDeMesure,
    TypeDeSuivi,
    TypeDExploitant,
    TypeEquipement,
    TypeEvenement,
)

MODELS_CONFIG = [
    # Vague 1 — aucune FK vers autre nomenclature
    {
        "label": "suivi_pasto.production",
        "cls": Production,
        "pk": "id_production",
        "natural_key": ["description"],
        "fks": [],
    },
    {
        "label": "suivi_pasto.categoriepension",
        "cls": CategoriePension,
        "pk": "id_categorie_pension",
        "natural_key": ["description"],
        "fks": [],
    },
    {
        "label": "suivi_pasto.espece",
        "cls": Espece,
        "pk": "id_espece",
        "natural_key": ["description"],
        "fks": [],
    },
    {
        "label": "suivi_pasto.typeconvention",
        "cls": TypeConvention,
        "pk": "id_type_convention",
        "natural_key": ["description"],
        "fks": [],
    },
    {
        "label": "suivi_pasto.typedexploitant",
        "cls": TypeDExploitant,
        "pk": "id_type_exploitant",
        "natural_key": ["description"],
        "fks": [],
    },
    {
        "label": "suivi_pasto.typeequipement",
        "cls": TypeEquipement,
        "pk": "id_type_equipement",
        "natural_key": ["description"],
        "fks": [],
    },
    {
        "label": "suivi_pasto.typedesuivi",
        "cls": TypeDeSuivi,
        "pk": "id_type_suivi",
        "natural_key": ["description"],
        "fks": [],
    },
    {
        "label": "suivi_pasto.typedemesure",
        "cls": TypeDeMesure,
        "pk": "id_type_mesure",
        "natural_key": ["description"],
        "fks": [],
    },
    {
        "label": "suivi_pasto.enjeu",
        "cls": Enjeu,
        "pk": "id_enjeu",
        "natural_key": ["description"],
        "fks": [],
    },
    {
        "label": "suivi_pasto.typeevenement",
        "cls": TypeEvenement,
        "pk": "id_type_evenement",
        "natural_key": ["description"],
        "fks": [],
    },
    {
        "label": "suivi_pasto.commodite",
        "cls": Commodite,
        "pk": "id_commodite",
        "natural_key": ["description"],
        "fks": [],
    },
    # Vague 2 — FK vers Espece
    {
        "label": "suivi_pasto.race",
        "cls": Race,
        "pk": "id_race",
        "natural_key": ["description", "espece_id"],
        "fks": [{"field": "espece_id", "ref": "suivi_pasto.espece"}],
    },
    {
        "label": "suivi_pasto.categorieanimaux",
        "cls": CategorieAnimaux,
        "pk": "id_categorie_animaux",
        "natural_key": ["description", "espece_id"],
        "fks": [{"field": "espece_id", "ref": "suivi_pasto.espece"}],
    },
]


class Command(BaseCommand):
    help = (
        "Importe les référentiels (nomenclatures) depuis un fichier produit par "
        "dumpdata ou export_referentiels. Les IDs sources sont remappés, les FK "
        "inter-nomenclatures résolues, et les séquences PostgreSQL repositionnées."
    )

    def add_arguments(self, parser):
        parser.add_argument("fichier", help="Chemin vers le fichier JSON source")
        parser.add_argument(
            "--update",
            action="store_true",
            help="Met à jour les champs si l'enregistrement existe déjà (défaut : ignorer)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simule l'import sans écrire en base",
        )
        parser.add_argument(
            "--created-by",
            metavar="USERNAME",
            help="Valeur à inscrire dans created_by pour les enregistrements créés",
        )
        parser.add_argument(
            "--output-map",
            metavar="FICHIER",
            help="Écrit la carte de remapping des IDs (source → cible) dans ce fichier JSON",
        )

    def handle(self, **options):
        _disable_auditlog()

        path = options["fichier"]
        do_update = options["update"]
        dry_run = options["dry_run"]
        created_by = options.get("created_by")
        output_map_path = options.get("output_map")

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f"Fichier introuvable : {path}")
        except json.JSONDecodeError as e:
            raise CommandError(f"JSON invalide : {e}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("Mode dry-run — aucune écriture en base\n")
            )

        # id_map[model_label][source_pk] = target_pk
        id_map: dict[str, dict[int, int]] = {cfg["label"]: {} for cfg in MODELS_CONFIG}

        # Index entries par model label pour accès O(1)
        entries_by_model: dict[str, list] = {cfg["label"]: [] for cfg in MODELS_CONFIG}
        unknown_models = set()
        for entry in data:
            label = entry.get("model", "")
            if label in entries_by_model:
                entries_by_model[label].append(entry)
            else:
                unknown_models.add(label)

        if unknown_models:
            self.stdout.write(
                self.style.WARNING(
                    f"Modèles ignorés (non gérés) : {', '.join(sorted(unknown_models))}"
                )
            )

        with transaction.atomic():
            for cfg in MODELS_CONFIG:
                label = cfg["label"]
                cls = cfg["cls"]
                pk_field = cfg["pk"]
                natural_key_fields = cfg["natural_key"]
                fk_defs = cfg["fks"]

                created_count = updated_count = skipped_count = 0

                for entry in entries_by_model[label]:
                    source_pk = entry["pk"]
                    fields = dict(entry["fields"])

                    # Résolution des FK : remplacer les PKs sources par les PKs cibles
                    for fk in fk_defs:
                        fk_field = fk["field"]
                        ref_label = fk["ref"]
                        # Le JSON dumpdata stocke la FK sous le nom du champ sans "_id"
                        json_fk_key = fk_field.removesuffix("_id")
                        source_fk_val = fields.pop(json_fk_key, None)
                        if source_fk_val is None:
                            fields[fk_field] = None
                        else:
                            target_fk_val = id_map[ref_label].get(source_fk_val)
                            if target_fk_val is None:
                                self.stdout.write(
                                    self.style.ERROR(
                                        f"  {label} pk={source_pk} : FK {json_fk_key}={source_fk_val} "
                                        f"non résolue dans {ref_label} — enregistrement ignoré"
                                    )
                                )
                                continue
                            fields[fk_field] = target_fk_val

                    # Exclure les champs audit (gérés automatiquement)
                    for audit_field in (
                        "created_by",
                        "created_on",
                        "modified_by",
                        "modified_on",
                    ):
                        fields.pop(audit_field, None)

                    # Construire le filtre par clé naturelle
                    natural_filter = {
                        k: fields[k] for k in natural_key_fields if k in fields
                    }

                    try:
                        existing = cls.objects.get(**natural_filter)
                        target_pk = getattr(existing, pk_field)
                        id_map[label][source_pk] = target_pk

                        if do_update:
                            if not dry_run:
                                for k, v in fields.items():
                                    setattr(existing, k, v)
                                existing.save()
                            updated_count += 1
                        else:
                            skipped_count += 1

                    except cls.DoesNotExist:
                        if not dry_run:
                            if created_by:
                                fields["created_by"] = created_by
                            obj = cls(**fields)
                            obj.save()
                            target_pk = getattr(obj, pk_field)
                        else:
                            # En dry-run on simule un PK fictif pour ne pas bloquer la résolution FK
                            target_pk = -(source_pk)
                        id_map[label][source_pk] = target_pk
                        created_count += 1

                self.stdout.write(
                    f"{cls.__name__:<22} : {created_count} créés, "
                    f"{updated_count} mis à jour, {skipped_count} ignorés"
                )

            if not dry_run:
                self._reset_sequences()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nSéquences repositionnées : {len(MODELS_CONFIG)} tables"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING("\nDry-run terminé — séquences non modifiées")
                )

        if output_map_path:
            serializable_map = {
                label: {str(k): v for k, v in mapping.items()}
                for label, mapping in id_map.items()
            }
            with open(output_map_path, "w", encoding="utf-8") as f:
                json.dump(serializable_map, f, indent=2, ensure_ascii=False)
            self.stdout.write(
                self.style.SUCCESS(f"Carte de remapping écrite dans {output_map_path}")
            )

    def _reset_sequences(self):
        with connection.cursor() as cur:
            for cfg in MODELS_CONFIG:
                table = cfg["cls"]._meta.db_table
                pk = cfg["pk"]
                cur.execute(
                    f"SELECT setval(pg_get_serial_sequence(%s, %s), COALESCE(MAX({pk}), 1), true) FROM {table}",
                    [table, pk],
                )
