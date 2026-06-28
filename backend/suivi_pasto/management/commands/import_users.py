import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection, transaction
from django.core.management.base import BaseCommand, CommandError
from auditlog.registry import auditlog as auditlog_registry


def _disable_auditlog():
    for model in list(auditlog_registry.get_models()):
        auditlog_registry.unregister(model)


User = get_user_model()


class Command(BaseCommand):
    help = (
        "Importe les utilisateurs depuis un fichier produit par export_users. "
        "Les groupes sont assignés par nom (import_groups doit avoir été exécuté avant). "
        "Produit une carte username → new_id utilisable par import_up_data."
    )

    def add_arguments(self, parser):
        parser.add_argument("fichier", help="Chemin vers le fichier JSON source")
        parser.add_argument(
            "--output-map",
            metavar="FICHIER",
            help="Écrit la carte username → new_id dans ce fichier JSON",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Met à jour les champs si l'utilisateur existe déjà (défaut : ignorer)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simule l'import sans écrire en base",
        )

    def handle(self, **options):
        path = options["fichier"]
        output_map_path = options.get("output_map")
        do_update = options["update"]
        dry_run = options["dry_run"]

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f"Fichier introuvable : {path}")
        except json.JSONDecodeError as e:
            raise CommandError(f"JSON invalide : {e}")

        _disable_auditlog()

        if dry_run:
            self.stdout.write(
                self.style.WARNING("Mode dry-run — aucune écriture en base\n")
            )

        user_id_map = {}
        created_count = updated_count = skipped_count = 0

        with transaction.atomic():
            for entry in data:
                username = entry["username"]

                # Résoudre les groupes
                group_names = entry.get("groups", [])
                groups = []
                for name in group_names:
                    try:
                        groups.append(Group.objects.get(name=name))
                    except Group.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Groupe '{name}' introuvable pour {username} — ignoré"
                            )
                        )

                existing = User.objects.filter(username=username).first()

                if existing:
                    user_id_map[username] = existing.id
                    if do_update:
                        if not dry_run:
                            existing.email = entry["email"]
                            existing.password = entry["password"]
                            existing.first_name = entry["first_name"]
                            existing.last_name = entry["last_name"]
                            existing.is_staff = entry["is_staff"]
                            existing.is_superuser = entry["is_superuser"]
                            existing.is_active = entry["is_active"]
                            existing.save()
                            existing.groups.set(groups)
                        updated_count += 1
                        self.stdout.write(f"  {username} — mis à jour")
                    else:
                        skipped_count += 1
                        self.stdout.write(f"  {username} — existe déjà, ignoré")
                    continue

                if not dry_run:
                    user = User(
                        username=username,
                        email=entry["email"],
                        first_name=entry["first_name"],
                        last_name=entry["last_name"],
                        is_staff=entry["is_staff"],
                        is_superuser=entry["is_superuser"],
                        is_active=entry["is_active"],
                    )
                    user.password = entry["password"]
                    user.save()
                    user.groups.set(groups)
                    user_id_map[username] = user.id
                    self.stdout.write(f"  {username} — créé (id={user.id})")
                else:
                    user_id_map[username] = None
                    self.stdout.write(f"  {username} — serait créé")

                created_count += 1

            if not dry_run:
                self._reset_sequence()
                self.stdout.write(
                    self.style.SUCCESS("Séquence auth_user repositionnée")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n{created_count} créés, {updated_count} mis à jour, {skipped_count} ignorés"
            )
        )

        if output_map_path:
            with open(output_map_path, "w", encoding="utf-8") as f:
                json.dump(user_id_map, f, indent=2, ensure_ascii=False)
            self.stdout.write(
                self.style.SUCCESS(f"Carte users écrite dans {output_map_path}")
            )

    def _reset_sequence(self):
        table = User._meta.db_table
        pk_col = User._meta.pk.column
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT setval(pg_get_serial_sequence(%s, %s), COALESCE(MAX({pk_col}), 1), true) FROM {table}",
                [table, pk_col],
            )
