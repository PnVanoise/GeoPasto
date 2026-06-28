import json

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.db import connection, transaction
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from auditlog.registry import auditlog as auditlog_registry


def _disable_auditlog():
    for model in list(auditlog_registry.get_models()):
        auditlog_registry.unregister(model)


from suivi_pasto.models import UnitePastorale, GeometrieUnitePastorale


class Command(BaseCommand):
    help = (
        "Importe les unités pastorales depuis un shapefile. "
        "Crée UnitePastorale + GeometrieUnitePastorale (géométrie initiale) pour chaque feature. "
        "Produit une carte code_up → new_id utilisable par import_up_data."
    )

    def add_arguments(self, parser):
        parser.add_argument("shapefile", help="Chemin vers le fichier .shp")
        parser.add_argument(
            "--field-map",
            metavar="MAPPING",
            default="",
            help=(
                "Mapping champ_django=COLONNE_SHP séparés par des virgules. "
                "Ex : code_up=CODE,nom_up=NOM,secteur=SECTEUR. "
                "Champs non spécifiés : même nom que le champ Django."
            ),
        )
        parser.add_argument(
            "--date-debut",
            metavar="YYYY-MM-DD",
            default=None,
            help="Date de début de validité de la géométrie (défaut : aujourd'hui)",
        )
        parser.add_argument(
            "--output-map",
            metavar="FICHIER",
            help="Écrit la carte code_up → new_id dans ce fichier JSON",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simule l'import sans écrire en base",
        )
        parser.add_argument(
            "--created-by",
            metavar="USERNAME",
            help="Valeur à inscrire dans created_by",
        )

    def handle(self, **options):
        shp_path = options["shapefile"]
        field_map_str = options["field_map"]
        output_map_path = options.get("output_map")
        dry_run = options["dry_run"]
        created_by = options.get("created_by") or ""

        if options["date_debut"]:
            from datetime import date

            date_debut = date.fromisoformat(options["date_debut"])
        else:
            date_debut = timezone.now().date()

        # Parse field mapping
        col_map = {}
        if field_map_str:
            for pair in field_map_str.split(","):
                pair = pair.strip()
                if "=" not in pair:
                    raise CommandError(
                        f"Mapping invalide : '{pair}' (format attendu : django_field=SHP_COLUMN)"
                    )
                django_field, shp_col = pair.split("=", 1)
                col_map[django_field.strip()] = shp_col.strip()

        def shp_field(django_name):
            return col_map.get(django_name, django_name)

        _disable_auditlog()

        if dry_run:
            self.stdout.write(
                self.style.WARNING("Mode dry-run — aucune écriture en base\n")
            )

        try:
            ds = DataSource(shp_path)
        except Exception as e:
            raise CommandError(f"Impossible d'ouvrir le shapefile : {e}")

        layer = ds[0]
        self.stdout.write(
            f"Shapefile : {layer.num_feat} features, CRS source : {layer.srs}"
        )

        # Vérification des colonnes disponibles
        available = layer.fields
        for django_field in ("code_up", "nom_up"):
            col = shp_field(django_field)
            if col not in available:
                raise CommandError(
                    f"Colonne '{col}' (pour {django_field}) absente du shapefile. "
                    f"Colonnes disponibles : {list(available)}"
                )

        up_id_map = {}
        created_count = skipped_count = 0

        with transaction.atomic():
            for feature in layer:
                code_up = str(feature[shp_field("code_up")].value or "").strip()
                nom_up = str(feature[shp_field("nom_up")].value or "").strip()
                secteur_col = shp_field("secteur")
                secteur = (
                    str(feature[secteur_col].value or "").strip()
                    if secteur_col in available
                    else None
                )

                if not code_up:
                    self.stdout.write(
                        self.style.WARNING(f"Feature sans code_up ignorée")
                    )
                    continue

                # Géométrie : transform vers SRID 2154
                ogr_geom = feature.geom
                ogr_geom.transform(2154)
                geos_geom = GEOSGeometry(ogr_geom.wkt, srid=2154)
                if geos_geom.geom_type == "Polygon":
                    geos_geom = MultiPolygon(geos_geom)
                elif geos_geom.geom_type != "MultiPolygon":
                    self.stdout.write(
                        self.style.WARNING(
                            f"UP {code_up} : type de géométrie inattendu ({geos_geom.geom_type}), ignorée"
                        )
                    )
                    continue

                existing = UnitePastorale.objects.filter(code_up=code_up).first()
                if existing:
                    up_id_map[code_up] = existing.id_unite_pastorale
                    skipped_count += 1
                    self.stdout.write(
                        f"  UP {code_up} — existe déjà (id={existing.id_unite_pastorale}), ignorée"
                    )
                    continue

                if not dry_run:
                    up = UnitePastorale(
                        code_up=code_up,
                        nom_up=nom_up,
                        secteur=secteur,
                        created_by=created_by,
                    )
                    up.save()

                    GeometrieUnitePastorale(
                        unite_pastorale=up,
                        geometry=geos_geom,
                        date_debut_validite=date_debut,
                        date_fin_validite=None,
                        created_by=created_by,
                    ).save()

                    up_id_map[code_up] = up.id_unite_pastorale
                    self.stdout.write(
                        f"  UP {code_up} — créée (id={up.id_unite_pastorale})"
                    )
                else:
                    up_id_map[code_up] = None
                    self.stdout.write(f"  UP {code_up} — serait créée")

                created_count += 1

            if not dry_run:
                self._reset_sequences()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n{created_count} UP(s) créées, {skipped_count} ignorées (déjà existantes)"
            )
        )

        if output_map_path:
            with open(output_map_path, "w", encoding="utf-8") as f:
                json.dump(up_id_map, f, indent=2, ensure_ascii=False)
            self.stdout.write(
                self.style.SUCCESS(f"Carte UP écrite dans {output_map_path}")
            )

    def _reset_sequences(self):
        with connection.cursor() as cur:
            for cls in (UnitePastorale, GeometrieUnitePastorale):
                table = cls._meta.db_table
                pk = cls._meta.pk.column
                cur.execute(
                    f"SELECT setval(pg_get_serial_sequence(%s, %s), COALESCE(MAX({pk}), 1), true) FROM {table}",
                    [table, pk],
                )
