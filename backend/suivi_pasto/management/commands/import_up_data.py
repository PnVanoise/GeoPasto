import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection, transaction
from django.core.management.base import BaseCommand, CommandError
from auditlog.registry import auditlog as auditlog_registry


def _disable_auditlog():
    for model in list(auditlog_registry.get_models()):
        auditlog_registry.unregister(model)


from suivi_pasto.models import (
    AbriDUrgence,
    AbriDUrgenceCommodite,
    Berger,
    BeneficierDe,
    Cheptel,
    ConventionDExploitation,
    EquipementAlpage,
    EquipementExploitant,
    EtreCompose,
    Eleveur,
    Evenement,
    Exploitant,
    Exploiter,
    GardeSituation,
    Logement,
    MesureDePlan,
    PlanDeSuivi,
    ProprietaireFoncier,
    ProprietaireUnitePastorale,
    QuartierPasto,
    RealisationMesure,
    Ruche,
    SituationDExploitation,
    SubventionPNV,
    UnitePastorale,
    Visite,
)

User = get_user_model()


def _load_json(path, label):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise CommandError(f"Fichier introuvable ({label}) : {path}")
    except json.JSONDecodeError as e:
        raise CommandError(f"JSON invalide ({label}) : {e}")


def _resolve_geom(value):
    if value is None:
        return None
    return GEOSGeometry(value)


def _to_decimal(value):
    if value is None:
        return None
    return Decimal(str(value))


class Command(BaseCommand):
    help = (
        "Importe les données d'UPs depuis un fichier produit par export_up_data. "
        "Nécessite les cartes de remapping produites par import_referentiels, "
        "import_up_shapefile et import_users."
    )

    def add_arguments(self, parser):
        parser.add_argument("fichier", help="Fichier JSON produit par export_up_data")
        parser.add_argument(
            "--ref-map",
            required=True,
            metavar="FICHIER",
            help="Carte ref_id_map.json produite par import_referentiels --output-map",
        )
        parser.add_argument(
            "--up-map",
            required=True,
            metavar="FICHIER",
            help="Carte up_id_map.json produite par import_up_shapefile --output-map",
        )
        parser.add_argument(
            "--user-map",
            required=True,
            metavar="FICHIER",
            help="Carte user_id_map.json produite par import_users --output-map",
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="Simule l'import sans écrire en base"
        )
        parser.add_argument(
            "--created-by",
            metavar="USERNAME",
            help="Valeur à inscrire dans created_by si absent des données sources",
        )

    def handle(self, **options):
        _disable_auditlog()

        dry_run = options["dry_run"]
        created_by_default = options.get("created_by") or ""

        data = _load_json(options["fichier"], "export_up_data")
        ref_map = _load_json(options["ref_map"], "ref_id_map")
        up_id_map = _load_json(options["up_map"], "up_id_map")
        user_id_map = _load_json(options["user_map"], "user_id_map")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("Mode dry-run — aucune écriture en base\n")
            )

        sections = data.get("sections", {})

        # Construire la carte old_up_pk → new_up_pk depuis UnitePastorale export + up_id_map
        old_up_pk_to_new = {}
        for entry in sections.get("UnitePastorale", []):
            code_up = entry["code_up"]
            old_pk = entry["pk"]
            new_pk = up_id_map.get(code_up)
            if new_pk is None:
                raise CommandError(
                    f"UP '{code_up}' (pk={old_pk}) absente de la carte up_id_map. "
                    f"Avez-vous bien exécuté import_up_shapefile ?"
                )
            old_up_pk_to_new[old_pk] = new_pk

        # Maps locales : model_name → {old_pk: new_pk}
        local = {}

        def resolve_fk(value, map_type, ref_label=None, local_key=None, nullable=False):
            if value is None:
                return None
            if map_type == "ref":
                new_val = ref_map.get(ref_label, {}).get(str(value))
                if new_val is None and not nullable:
                    raise CommandError(
                        f"FK référentiel non résolue : label={ref_label} pk={value}"
                    )
                return new_val
            if map_type == "up":
                new_val = old_up_pk_to_new.get(value)
                if new_val is None and not nullable:
                    raise CommandError(f"FK UP non résolue : old_pk={value}")
                return new_val
            if map_type == "local":
                new_val = local.get(local_key, {}).get(value)
                if new_val is None and not nullable:
                    raise CommandError(
                        f"FK locale non résolue : model={local_key} pk={value}"
                    )
                return new_val
            if map_type == "user":
                return user_id_map.get(value)
            return value

        def import_section(
            section_key,
            model_cls,
            pk_field,
            fk_specs,
            geo_fields=None,
            created_by=created_by_default,
        ):
            """
            fk_specs : liste de dicts {field, type, ref_label?, local_key?, nullable?}
            geo_fields : liste de noms de champs géométrie
            """
            geo_fields = geo_fields or []
            entries = sections.get(section_key, [])
            local.setdefault(section_key, {})
            created = skipped = 0

            for entry in entries:
                old_pk = entry["pk"]
                fields = dict(entry["fields"])

                # Résoudre les FKs
                for spec in fk_specs:
                    field = spec["field"]
                    nullable = spec.get("nullable", False)
                    raw = fields.get(field)
                    if raw is None and nullable:
                        fields[field] = None
                        continue
                    fields[field] = resolve_fk(
                        raw,
                        spec["type"],
                        ref_label=spec.get("ref_label"),
                        local_key=spec.get("local_key"),
                        nullable=nullable,
                    )

                # Résoudre les géométries
                for gf in geo_fields:
                    fields[gf] = _resolve_geom(fields.get(gf))

                # Audit
                if not fields.get("created_by"):
                    fields["created_by"] = created_by

                if not dry_run:
                    obj = model_cls(**{k: v for k, v in fields.items()})
                    obj.save()
                    new_pk = getattr(obj, pk_field)
                else:
                    new_pk = -(old_pk)

                local[section_key][old_pk] = new_pk
                created += 1

            if not dry_run:
                self._reset_seq(model_cls)

            verb = "importés" if not dry_run else "simulés"
            self.stdout.write(
                f"  {section_key:<35} : {created} {verb}, {skipped} ignorés"
            )
            return created

        with transaction.atomic():

            import_section(
                "ProprietaireFoncier", ProprietaireFoncier, "id_proprietaire", []
            )

            import_section("Eleveur", Eleveur, "id_eleveur", [])

            import_section(
                "Exploitant",
                Exploitant,
                "id_exploitant",
                [
                    {
                        "field": "type_exploitant_id",
                        "type": "ref",
                        "ref_label": "suivi_pasto.typedexploitant",
                        "nullable": True,
                    },
                    {
                        "field": "president_id",
                        "type": "local",
                        "local_key": "Eleveur",
                        "nullable": True,
                    },
                ],
            )

            import_section(
                "EtreCompose",
                EtreCompose,
                "id_etre_compose",
                [
                    {
                        "field": "exploitant_id",
                        "type": "local",
                        "local_key": "Exploitant",
                        "nullable": True,
                    },
                    {
                        "field": "eleveur_id",
                        "type": "local",
                        "local_key": "Eleveur",
                        "nullable": True,
                    },
                    {
                        "field": "exploitant_membre_id",
                        "type": "local",
                        "local_key": "Exploitant",
                        "nullable": True,
                    },
                ],
            )

            import_section("Berger", Berger, "id_berger", [])

            import_section(
                "ProprietaireUnitePastorale",
                ProprietaireUnitePastorale,
                "id_proprietaire_up",
                [
                    {
                        "field": "proprietaire_id",
                        "type": "local",
                        "local_key": "ProprietaireFoncier",
                        "nullable": True,
                    },
                    {"field": "unite_pastorale_id", "type": "up", "nullable": True},
                ],
            )

            import_section(
                "SituationDExploitation",
                SituationDExploitation,
                "id_situation",
                [
                    {"field": "unite_pastorale_id", "type": "up", "nullable": True},
                    {
                        "field": "exploitant_id",
                        "type": "local",
                        "local_key": "Exploitant",
                        "nullable": True,
                    },
                ],
            )

            import_section(
                "ConventionDExploitation",
                ConventionDExploitation,
                "id_convention",
                [
                    {"field": "unite_pastorale_id", "type": "up", "nullable": True},
                    {
                        "field": "exploitant_id",
                        "type": "local",
                        "local_key": "Exploitant",
                        "nullable": True,
                    },
                    {
                        "field": "type_convention_id",
                        "type": "ref",
                        "ref_label": "suivi_pasto.typeconvention",
                        "nullable": True,
                    },
                ],
                geo_fields=["geometry"],
            )

            import_section(
                "Cheptel",
                Cheptel,
                "id_cheptel",
                [
                    {
                        "field": "situation_exploitation_id",
                        "type": "local",
                        "local_key": "SituationDExploitation",
                        "nullable": True,
                    },
                    {
                        "field": "eleveur_id",
                        "type": "local",
                        "local_key": "Eleveur",
                        "nullable": True,
                    },
                    {
                        "field": "exploitant_proprietaire_id",
                        "type": "local",
                        "local_key": "Exploitant",
                        "nullable": True,
                    },
                    {
                        "field": "production_id",
                        "type": "ref",
                        "ref_label": "suivi_pasto.production",
                        "nullable": True,
                    },
                    {
                        "field": "pension_id",
                        "type": "ref",
                        "ref_label": "suivi_pasto.categoriepension",
                        "nullable": True,
                    },
                    {
                        "field": "race_id",
                        "type": "ref",
                        "ref_label": "suivi_pasto.race",
                        "nullable": True,
                    },
                    {
                        "field": "categorie_animaux_id",
                        "type": "ref",
                        "ref_label": "suivi_pasto.categorieanimaux",
                        "nullable": True,
                    },
                ],
            )

            import_section(
                "QuartierPasto",
                QuartierPasto,
                "id_quartier",
                [
                    {
                        "field": "situation_exploitation_id",
                        "type": "local",
                        "local_key": "SituationDExploitation",
                        "nullable": True,
                    },
                ],
                geo_fields=["geometry"],
            )

            import_section(
                "Exploiter",
                Exploiter,
                "id_exploiter",
                [
                    {
                        "field": "cheptel_id",
                        "type": "local",
                        "local_key": "Cheptel",
                        "nullable": True,
                    },
                    {
                        "field": "quartier_id",
                        "type": "local",
                        "local_key": "QuartierPasto",
                        "nullable": True,
                    },
                ],
            )

            import_section(
                "GardeSituation",
                GardeSituation,
                "id_garde_situation",
                [
                    {
                        "field": "situation_exploitation_id",
                        "type": "local",
                        "local_key": "SituationDExploitation",
                        "nullable": True,
                    },
                    {
                        "field": "berger_id",
                        "type": "local",
                        "local_key": "Berger",
                        "nullable": True,
                    },
                ],
            )

            import_section(
                "Ruche",
                Ruche,
                "id_ruche",
                [
                    {
                        "field": "situation_exploitation_id",
                        "type": "local",
                        "local_key": "SituationDExploitation",
                        "nullable": True,
                    },
                ],
                geo_fields=["geometry"],
            )

            import_section(
                "PlanDeSuivi",
                PlanDeSuivi,
                "id_plan_suivi",
                [
                    {"field": "unite_pastorale_id", "type": "up", "nullable": True},
                    {
                        "field": "type_suivi_id",
                        "type": "ref",
                        "ref_label": "suivi_pasto.typedesuivi",
                        "nullable": True,
                    },
                ],
            )

            import_section(
                "MesureDePlan",
                MesureDePlan,
                "id_mesure_plan",
                [
                    {
                        "field": "plan_suivi_id",
                        "type": "local",
                        "local_key": "PlanDeSuivi",
                        "nullable": True,
                    },
                    {
                        "field": "type_mesure_id",
                        "type": "ref",
                        "ref_label": "suivi_pasto.typedemesure",
                        "nullable": True,
                    },
                ],
                geo_fields=["geometry"],
            )

            # M2M MesureDePlan ↔ Enjeu
            mp_enjeu_count = 0
            for row in sections.get("MesureDePlan_enjeux", []):
                new_mp_pk = local["MesureDePlan"].get(row["mesure_plan_pk"])
                new_enjeu_pk = ref_map.get("suivi_pasto.enjeu", {}).get(
                    str(row["enjeu_pk"])
                )
                if new_mp_pk and new_enjeu_pk and not dry_run:
                    mp = MesureDePlan.objects.get(pk=new_mp_pk)
                    mp.enjeux.add(new_enjeu_pk)
                mp_enjeu_count += 1
            self.stdout.write(
                f"  {'MesureDePlan_enjeux':<35} : {mp_enjeu_count} liaisons"
            )

            import_section(
                "RealisationMesure",
                RealisationMesure,
                "id_realisation_mesure",
                [
                    {
                        "field": "mesure_plan_id",
                        "type": "local",
                        "local_key": "MesureDePlan",
                    },
                    {
                        "field": "situation_id",
                        "type": "local",
                        "local_key": "SituationDExploitation",
                    },
                ],
            )

            import_section(
                "Evenement",
                Evenement,
                "id_evenement",
                [
                    {
                        "field": "situation_id",
                        "type": "local",
                        "local_key": "SituationDExploitation",
                        "nullable": True,
                    },
                    {
                        "field": "mesure_plan_id",
                        "type": "local",
                        "local_key": "MesureDePlan",
                        "nullable": True,
                    },
                    {
                        "field": "type_evenement_id",
                        "type": "ref",
                        "ref_label": "suivi_pasto.typeevenement",
                        "nullable": True,
                    },
                ],
                geo_fields=["geometry"],
            )

            import_section(
                "Visite",
                Visite,
                "id_visite",
                [
                    {"field": "unite_pastorale_id", "type": "up"},
                ],
            )

            # M2M Visite ↔ Eleveur
            ve_count = 0
            for row in sections.get("Visite_contacts_alpagistes", []):
                new_v_pk = local["Visite"].get(row["visite_pk"])
                new_e_pk = local["Eleveur"].get(row["eleveur_pk"])
                if new_v_pk and new_e_pk and not dry_run:
                    v = Visite.objects.get(pk=new_v_pk)
                    v.contacts_alpagistes.add(new_e_pk)
                ve_count += 1
            self.stdout.write(
                f"  {'Visite_contacts_alpagistes':<35} : {ve_count} liaisons"
            )

            # M2M Visite ↔ User (par username)
            vu_count = 0
            for row in sections.get("Visite_observateurs", []):
                new_v_pk = local["Visite"].get(row["visite_pk"])
                new_u_pk = user_id_map.get(row["username"])
                if new_v_pk and new_u_pk and not dry_run:
                    v = Visite.objects.get(pk=new_v_pk)
                    v.observateurs.add(new_u_pk)
                vu_count += 1
            self.stdout.write(f"  {'Visite_observateurs':<35} : {vu_count} liaisons")

            import_section(
                "EquipementAlpage",
                EquipementAlpage,
                "id_equipement_alpage",
                [
                    {"field": "unite_pastorale_id", "type": "up", "nullable": True},
                    {
                        "field": "type_equipement_id",
                        "type": "ref",
                        "ref_label": "suivi_pasto.typeequipement",
                        "nullable": True,
                    },
                ],
                geo_fields=["geometry"],
            )

            import_section("AbriDUrgence", AbriDUrgence, "id_abri_urgence", [])

            import_section(
                "BeneficierDe",
                BeneficierDe,
                "id_beneficier_de",
                [
                    {
                        "field": "exploitant_id",
                        "type": "local",
                        "local_key": "Exploitant",
                        "nullable": True,
                    },
                    {
                        "field": "abri_urgence_id",
                        "type": "local",
                        "local_key": "AbriDUrgence",
                        "nullable": True,
                    },
                ],
                geo_fields=["geometry"],
            )

            import_section(
                "EquipementExploitant",
                EquipementExploitant,
                "id_equipement_exploitant",
                [
                    {
                        "field": "situation_exploitation_id",
                        "type": "local",
                        "local_key": "SituationDExploitation",
                        "nullable": True,
                    },
                    {
                        "field": "type_equipement_id",
                        "type": "ref",
                        "ref_label": "suivi_pasto.typeequipement",
                        "nullable": True,
                    },
                    {
                        "field": "beneficier_de_id",
                        "type": "local",
                        "local_key": "BeneficierDe",
                        "nullable": True,
                    },
                ],
                geo_fields=["geometry"],
            )

            import_section(
                "AbriDUrgenceCommodite",
                AbriDUrgenceCommodite,
                "id_abri_urgence_commodite",
                [
                    {
                        "field": "abri_urgence_id",
                        "type": "local",
                        "local_key": "AbriDUrgence",
                        "nullable": True,
                    },
                    {
                        "field": "commodite_id",
                        "type": "ref",
                        "ref_label": "suivi_pasto.commodite",
                        "nullable": True,
                    },
                ],
            )

            import_section(
                "SubventionPNV",
                SubventionPNV,
                "id_subvention",
                [
                    {
                        "field": "exploitant_id",
                        "type": "local",
                        "local_key": "Exploitant",
                        "nullable": True,
                    },
                ],
            )

            import_section(
                "Logement",
                Logement,
                "id_logement",
                [
                    {"field": "unite_pastorale_id", "type": "up", "nullable": True},
                ],
                geo_fields=["geom"],
            )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\nDry-run terminé — aucune donnée écrite")
            )
        else:
            self.stdout.write(self.style.SUCCESS("\nImport terminé"))

    def _reset_seq(self, model_cls):
        table = model_cls._meta.db_table
        pk_col = model_cls._meta.pk.column
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT setval(pg_get_serial_sequence(%s, %s), COALESCE(MAX({pk_col}), 1), true) FROM {table}",
                [table, pk_col],
            )
