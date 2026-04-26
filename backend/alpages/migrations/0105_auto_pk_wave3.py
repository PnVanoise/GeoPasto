from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alpages', '0104_auto_pk_wave2'),
    ]

    operations = [
        # QuartierPasto
        migrations.AlterField(
            model_name='quartierpasto',
            name='id_quartier',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_quartierpasto','id_quartier'),
                    COALESCE(MAX(id_quartier), 1), true
                ) FROM alpages_quartierpasto;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Cheptel
        migrations.AlterField(
            model_name='cheptel',
            name='id_cheptel',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_cheptel','id_cheptel'),
                    COALESCE(MAX(id_cheptel), 1), true
                ) FROM alpages_cheptel;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # SituationDExploitation
        migrations.AlterField(
            model_name='situationdexploitation',
            name='id_situation',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_situationdexploitation','id_situation'),
                    COALESCE(MAX(id_situation), 1), true
                ) FROM alpages_situationdexploitation;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # UnitePastorale
        migrations.AlterField(
            model_name='unitepastorale',
            name='id_unite_pastorale',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_unitepastorale','id_unite_pastorale'),
                    COALESCE(MAX(id_unite_pastorale), 1), true
                ) FROM alpages_unitepastorale;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
