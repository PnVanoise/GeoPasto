from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("suivi_pasto", "0016_situationdexploitation_sans_gardiennage"),
    ]

    operations = [
        migrations.AddField(
            model_name="plandesuivi",
            name="plan_de_gestion",
            field=models.URLField(max_length=500, null=True, blank=True),
        ),
    ]
