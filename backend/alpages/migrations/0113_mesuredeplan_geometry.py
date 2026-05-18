from django.db import migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ("alpages", "0112_add_coefficient_ugb_to_categorie_animaux"),
    ]

    operations = [
        migrations.AddField(
            model_name="mesuredeplan",
            name="geometry",
            field=django.contrib.gis.db.models.fields.GeometryField(
                blank=True, null=True, srid=2154
            ),
        ),
    ]
