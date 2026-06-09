import json

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Importe les groupes et leurs permissions depuis un fichier produit par dumpdata auth.group."

    def add_arguments(self, parser):
        parser.add_argument(
            "fichier", help="Chemin vers le fichier JSON (groups_export.json)"
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Vide les permissions existantes du groupe avant d'importer",
        )

    def handle(self, *args, **options):
        path = options["fichier"]
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f"Fichier introuvable : {path}")
        except json.JSONDecodeError as e:
            raise CommandError(f"JSON invalide : {e}")

        for entry in data:
            if entry.get("model") != "auth.group":
                continue

            fields = entry["fields"]
            name = fields["name"]
            group, created = Group.objects.get_or_create(name=name)
            action = "créé" if created else "mis à jour"

            if options["clear"]:
                group.permissions.clear()

            assigned = 0
            skipped = []
            for perm_key in fields.get("permissions", []):
                codename = perm_key[0]
                perm = Permission.objects.filter(codename=codename).first()
                if perm:
                    group.permissions.add(perm)
                    assigned += 1
                else:
                    skipped.append(codename)

            msg = f'Groupe "{name}" ({action}) : {assigned} permissions assignées'
            if skipped:
                msg += f", {len(skipped)} ignorées : {', '.join(skipped)}"
            self.stdout.write(msg)
