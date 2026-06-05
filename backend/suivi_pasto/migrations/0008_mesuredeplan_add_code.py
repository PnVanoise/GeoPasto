from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("suivi_pasto", "0007_mesuredeplan_rename_dates_add_periode_realisation"),
    ]

    operations = [
        migrations.AddField(
            model_name="mesuredeplan",
            name="code",
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]
