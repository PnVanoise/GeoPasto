from django.db import migrations, models
import django.db.models.expressions
import django.db.models.functions


class Migration(migrations.Migration):

    dependencies = [
        ("suivi_pasto", "0006_enjeu_mesuredeplan_enjeux"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="mesuredeplan",
            name="chk_mesure_plan_periodes_coherentes",
        ),
        migrations.RenameField(
            model_name="mesuredeplan",
            old_name="debut_periode",
            new_name="date_debut_validite",
        ),
        migrations.RenameField(
            model_name="mesuredeplan",
            old_name="fin_periode",
            new_name="date_fin_validite",
        ),
        migrations.AddField(
            model_name="mesuredeplan",
            name="debut_periode_realisation",
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name="mesuredeplan",
            name="fin_periode_realisation",
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddConstraint(
            model_name="mesuredeplan",
            constraint=models.CheckConstraint(
                check=models.Q(date_fin_validite__isnull=True)
                | models.Q(date_debut_validite__lte=django.db.models.expressions.F("date_fin_validite")),
                name="chk_mesure_plan_validite_coherente",
            ),
        ),
    ]
