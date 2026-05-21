import datetime

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


def _populate_geometries(apps, schema_editor):
    UnitePastorale = apps.get_model("alpages", "UnitePastorale")
    GeometrieUnitePastorale = apps.get_model("alpages", "GeometrieUnitePastorale")

    for up in UnitePastorale.objects.filter(geom_active__isnull=False):
        annee = up.annee_version if up.annee_version else 2000
        GeometrieUnitePastorale.objects.create(
            unite_pastorale=up,
            geometry=up.geom_active,
            date_debut_validite=datetime.date(int(annee), 1, 1),
            date_fin_validite=None,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("alpages", "0114_realisationmesure"),
    ]

    operations = [
        # 1. Rendre geometry nullable avant de renommer
        migrations.AlterField(
            model_name="unitepastorale",
            name="geometry",
            field=django.contrib.gis.db.models.fields.MultiPolygonField(
                blank=True, null=True, srid=2154
            ),
        ),
        # 2. Renommer geometry → geom_active
        migrations.RenameField(
            model_name="unitepastorale",
            old_name="geometry",
            new_name="geom_active",
        ),
        # 3. Créer la table GeometrieUnitePastorale
        migrations.CreateModel(
            name="GeometrieUnitePastorale",
            fields=[
                (
                    "id_geometrie_up",
                    models.BigAutoField(primary_key=True, serialize=False),
                ),
                (
                    "created_by",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, null=True),
                ),
                (
                    "modified_by",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                (
                    "modified_on",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "geometry",
                    django.contrib.gis.db.models.fields.MultiPolygonField(srid=2154),
                ),
                ("date_debut_validite", models.DateField()),
                ("date_fin_validite", models.DateField(blank=True, null=True)),
                (
                    "unite_pastorale",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="geometries",
                        to="alpages.unitepastorale",
                    ),
                ),
            ],
            options={
                "verbose_name": "géométrie d'unité pastorale",
                "verbose_name_plural": "géométries d'unités pastorales",
                "ordering": ["-date_debut_validite"],
            },
        ),
        # 4. Data migration : une entrée par UP existante ayant une géométrie
        migrations.RunPython(
            _populate_geometries,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
