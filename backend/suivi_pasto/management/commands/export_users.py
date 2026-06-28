import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Exporte les utilisateurs actifs avec leurs groupes (par nom). "
        "Le fichier produit est utilisable par import_users sur une autre instance."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            metavar="FICHIER",
            help="Écrit le JSON dans ce fichier (défaut : stdout)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Inclure aussi les utilisateurs inactifs (défaut : actifs uniquement)",
        )

    def handle(self, **options):
        qs = User.objects.prefetch_related("groups")
        if not options["all"]:
            qs = qs.filter(is_active=True)

        data = []
        for user in qs.order_by("id"):
            data.append(
                {
                    "username": user.username,
                    "email": user.email,
                    "password": user.password,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "is_active": user.is_active,
                    "groups": [g.name for g in user.groups.all()],
                }
            )

        content = json.dumps(data, indent=2, ensure_ascii=False)

        output_path = options.get("output")
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.stdout.write(
                self.style.SUCCESS(
                    f"{len(data)} utilisateur(s) exportés dans {output_path}"
                )
            )
        else:
            self.stdout.write(content, ending="")
