import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("suivi_pasto", "0009_mesuredeplan_code_max_length_5"),
    ]
    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE suivi_pasto_quartierpasto
                ALTER COLUMN geometry TYPE geometry(MultiPolygon,2154)
                USING CASE WHEN geometry IS NULL THEN NULL ELSE ST_Multi(geometry) END;
            """,
            reverse_sql="""
                ALTER TABLE suivi_pasto_quartierpasto
                ALTER COLUMN geometry TYPE geometry(Polygon,2154)
                USING CASE WHEN geometry IS NULL THEN NULL
                           ELSE ST_GeometryN(geometry, 1) END;
            """,
        ),
        migrations.AlterField(
            model_name="quartierpasto",
            name="geometry",
            field=django.contrib.gis.db.models.fields.MultiPolygonField(
                blank=True, null=True, srid=2154
            ),
        ),
    ]
