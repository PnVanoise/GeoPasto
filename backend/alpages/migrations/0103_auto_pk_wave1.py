import django.db.models.deletion
import django.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alpages', '0102_named_pk_proprietaire_up_etrecompose_logement'),
    ]

    operations = [
        # SubventionPNV
        migrations.AlterField(
            model_name='subventionpnv',
            name='id_subvention',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_subventionpnv','id_subvention'),
                    COALESCE(MAX(id_subvention), 1), true
                ) FROM alpages_subventionpnv;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Commodite
        migrations.AlterField(
            model_name='commodite',
            name='id_commodite',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_commodite','id_commodite'),
                    COALESCE(MAX(id_commodite), 1), true
                ) FROM alpages_commodite;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # LogementCommodite
        migrations.AlterField(
            model_name='logementcommodite',
            name='id_logement_commodite',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_logementcommodite','id_logement_commodite'),
                    COALESCE(MAX(id_logement_commodite), 1), true
                ) FROM alpages_logementcommodite;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # AbriDUrgence
        migrations.AlterField(
            model_name='abridurgence',
            name='id_abri_urgence',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_abridurgence','id_abri_urgence'),
                    COALESCE(MAX(id_abri_urgence), 1), true
                ) FROM alpages_abridurgence;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # AbriDUrgenceCommodite
        migrations.AlterField(
            model_name='abridurgencecommodite',
            name='id_abri_urgence_commodite',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_abridurgencecommodite','id_abri_urgence_commodite'),
                    COALESCE(MAX(id_abri_urgence_commodite), 1), true
                ) FROM alpages_abridurgencecommodite;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # BeneficierDe
        migrations.AlterField(
            model_name='beneficierde',
            name='id_beneficier_de',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_beneficierde','id_beneficier_de'),
                    COALESCE(MAX(id_beneficier_de), 1), true
                ) FROM alpages_beneficierde;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Ruche
        migrations.AlterField(
            model_name='ruche',
            name='id_ruche',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_ruche','id_ruche'),
                    COALESCE(MAX(id_ruche), 1), true
                ) FROM alpages_ruche;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Berger
        migrations.AlterField(
            model_name='berger',
            name='id_berger',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_berger','id_berger'),
                    COALESCE(MAX(id_berger), 1), true
                ) FROM alpages_berger;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # GardeSituation
        migrations.AlterField(
            model_name='gardesituation',
            name='id_garde_situation',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_gardesituation','id_garde_situation'),
                    COALESCE(MAX(id_garde_situation), 1), true
                ) FROM alpages_gardesituation;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Exploiter
        migrations.AlterField(
            model_name='exploiter',
            name='id_exploiter',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_exploiter','id_exploiter'),
                    COALESCE(MAX(id_exploiter), 1), true
                ) FROM alpages_exploiter;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # ProprietaireFoncier
        migrations.AlterField(
            model_name='proprietairefoncier',
            name='id_proprietaire',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_proprietairefoncier','id_proprietaire'),
                    COALESCE(MAX(id_proprietaire), 1), true
                ) FROM alpages_proprietairefoncier;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # ConventionDExploitation
        migrations.AlterField(
            model_name='conventiondexploitation',
            name='id_convention',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_conventiondexploitation','id_convention'),
                    COALESCE(MAX(id_convention), 1), true
                ) FROM alpages_conventiondexploitation;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # EquipementAlpage
        migrations.AlterField(
            model_name='equipementalpage',
            name='id_equipement_alpage',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_equipementalpage','id_equipement_alpage'),
                    COALESCE(MAX(id_equipement_alpage), 1), true
                ) FROM alpages_equipementalpage;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # EquipementExploitant
        migrations.AlterField(
            model_name='equipementexploitant',
            name='id_equipement_exploitant',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('alpages_equipementexploitant','id_equipement_exploitant'),
                    COALESCE(MAX(id_equipement_exploitant), 1), true
                ) FROM alpages_equipementexploitant;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
