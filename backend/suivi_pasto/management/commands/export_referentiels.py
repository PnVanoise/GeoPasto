import io
import json

from django.core.management import call_command
from django.core.management.base import BaseCommand

REFERENTIEL_MODELS = [
    "suivi_pasto.production",
    "suivi_pasto.categoriepension",
    "suivi_pasto.espece",
    "suivi_pasto.race",
    "suivi_pasto.categorieanimaux",
    "suivi_pasto.typeconvention",
    "suivi_pasto.typedexploitant",
    "suivi_pasto.typeequipement",
    "suivi_pasto.typedesuivi",
    "suivi_pasto.typedemesure",
    "suivi_pasto.enjeu",
    "suivi_pasto.typeevenement",
    "suivi_pasto.commodite",
]


class Command(BaseCommand):
    help = (
        "Exporte les référentiels (nomenclatures) au format JSON dumpdata, "
        "utilisable comme source pour import_referentiels sur une autre instance."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            metavar="FICHIER",
            help="Écrit le JSON dans ce fichier (défaut : stdout)",
        )

    def handle(self, *args, **options):
        buf = io.StringIO()
        call_command(
            "dumpdata",
            *REFERENTIEL_MODELS,
            indent=2,
            stdout=buf,
        )
        content = buf.getvalue()

        output_path = options.get("output")
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            count = len(json.loads(content))
            self.stdout.write(
                self.style.SUCCESS(
                    f"{count} enregistrements exportés dans {output_path}"
                )
            )
        else:
            self.stdout.write(content, ending="")
