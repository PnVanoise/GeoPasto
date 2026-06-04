from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("suivi_pasto", "0008_mesuredeplan_add_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mesuredeplan",
            name="code",
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
