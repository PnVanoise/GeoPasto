from django.core.management.base import BaseCommand
from django.db.models import Q

from suivi_pasto.models import (
    UnitePastorale,
    GeometrieUnitePastorale,
    _refresh_geom_active,
)


class Command(BaseCommand):
    help = "Recalcule geom_active/active pour les UnitePastorale dont le cache est incohérent."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Recalculer toutes les UP, pas seulement les incohérentes",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Afficher les UP à corriger sans effectuer les modifications",
        )

    def handle(self, *args, **options):
        all_ups = options["all"]
        dry_run = options["dry_run"]

        if all_ups:
            ups = UnitePastorale.objects.all()
        else:
            # UPs avec geom_active non null mais aucune GeometrieUnitePastorale
            ups_sans_geom = UnitePastorale.objects.filter(
                geom_active__isnull=False
            ).exclude(
                id_unite_pastorale__in=GeometrieUnitePastorale.objects.values(
                    "unite_pastorale_id"
                )
            )
            # UPs avec active=True mais aucune géométrie couvrant aujourd'hui
            from django.utils import timezone

            today = timezone.now().date()
            ups_active_sans_geom_courante = UnitePastorale.objects.filter(
                active=True
            ).exclude(
                id_unite_pastorale__in=GeometrieUnitePastorale.objects.filter(
                    date_debut_validite__lte=today
                )
                .filter(
                    Q(date_fin_validite__isnull=True) | Q(date_fin_validite__gte=today)
                )
                .values("unite_pastorale_id")
            )
            ups = (ups_sans_geom | ups_active_sans_geom_courante).distinct()

        count = ups.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS("Aucune incohérence détectée."))
            return

        self.stdout.write(f"{count} UP à corriger :")
        for up in ups:
            self.stdout.write(
                f"  UP {up.pk} — {up.nom_up} "
                f"(geom_active={'oui' if up.geom_active else 'non'}, active={up.active})"
            )
            if not dry_run:
                _refresh_geom_active(up)
                up.refresh_from_db(fields=["geom_active", "active"])
                self.stdout.write(
                    f"    → corrigé : geom_active={'oui' if up.geom_active else 'non'}, active={up.active}"
                )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("Mode dry-run — aucune modification effectuée.")
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"{count} UP corrigées."))
