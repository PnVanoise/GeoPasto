from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alpages', '0103_auto_pk_wave1'),
    ]

    operations = [
        # MesureDePlan
        migrations.AlterField(
            model_name='mesuredeplan',
            name='id_mesure_plan',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_mesuredeplan','id_mesure_plan'),
                    COALESCE(MAX(id_mesure_plan), 1), true
                ) FROM alpages_mesuredeplan;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # PlanDeSuivi
        migrations.AlterField(
            model_name='plandesuivi',
            name='id_plan_suivi',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_plandesuivi','id_plan_suivi'),
                    COALESCE(MAX(id_plan_suivi), 1), true
                ) FROM alpages_plandesuivi;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Evenement
        migrations.AlterField(
            model_name='evenement',
            name='id_evenement',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_evenement','id_evenement'),
                    COALESCE(MAX(id_evenement), 1), true
                ) FROM alpages_evenement;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
