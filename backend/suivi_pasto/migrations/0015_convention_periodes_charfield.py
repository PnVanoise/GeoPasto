import django.db.models.deletion
from django.db import migrations, models


def dates_to_mm_dd(apps, schema_editor):
    ConventionDExploitation = apps.get_model("suivi_pasto", "ConventionDExploitation")
    for conv in ConventionDExploitation.objects.exclude(debut_periode_expl="").exclude(
        debut_periode_expl__isnull=True
    ):
        try:
            # YYYY-MM-DD → MM-DD
            parts = str(conv.debut_periode_expl).split("-")
            if len(parts) == 3:
                conv.debut_periode_expl = f"{parts[1]}-{parts[2]}"
                conv.save(update_fields=["debut_periode_expl"])
        except Exception:
            conv.debut_periode_expl = None
            conv.save(update_fields=["debut_periode_expl"])

    for conv in ConventionDExploitation.objects.exclude(fin_periode_expl="").exclude(
        fin_periode_expl__isnull=True
    ):
        try:
            parts = str(conv.fin_periode_expl).split("-")
            if len(parts) == 3:
                conv.fin_periode_expl = f"{parts[1]}-{parts[2]}"
                conv.save(update_fields=["fin_periode_expl"])
        except Exception:
            conv.fin_periode_expl = None
            conv.save(update_fields=["fin_periode_expl"])


class Migration(migrations.Migration):

    dependencies = [
        ("suivi_pasto", "0014_typemesure_types_suivi"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="conventiondexploitation",
            name="chk_convention_periodes_exploitation_coherentes",
        ),
        migrations.AlterField(
            model_name="conventiondexploitation",
            name="debut_periode_expl",
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name="conventiondexploitation",
            name="fin_periode_expl",
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.RunPython(dates_to_mm_dd, migrations.RunPython.noop),
    ]
