from django.core.management.base import BaseCommand
from alpages.models import UnitePastorale, _refresh_geom_active


class Command(BaseCommand):
    help = "Recalcule geom_active pour toutes les UnitePastorale selon l'historique des géométries"

    def handle(self, *args, **options):
        ups = UnitePastorale.objects.all()
        count = ups.count()
        for up in ups:
            _refresh_geom_active(up)
        self.stdout.write(self.style.SUCCESS(f"{count} UP traitées."))
