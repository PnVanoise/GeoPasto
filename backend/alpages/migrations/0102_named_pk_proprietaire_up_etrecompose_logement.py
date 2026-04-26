from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alpages', '0101_fix_typecheptel_contenttype'),
    ]

    operations = [
        # ProprietaireUnitePastorale : id → id_proprietaire_up (db_column='id', pas de SQL)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(
                    model_name='proprietaireunitepastorale',
                    old_name='id',
                    new_name='id_proprietaire_up',
                ),
                migrations.AlterField(
                    model_name='proprietaireunitepastorale',
                    name='id_proprietaire_up',
                    field=models.BigAutoField(primary_key=True, db_column='id', serialize=False),
                ),
            ],
            database_operations=[],
        ),

        # EtreCompose : id → id_etre_compose (db_column='id', pas de SQL)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(
                    model_name='etrecompose',
                    old_name='id',
                    new_name='id_etre_compose',
                ),
                migrations.AlterField(
                    model_name='etrecompose',
                    name='id_etre_compose',
                    field=models.BigAutoField(primary_key=True, db_column='id', serialize=False),
                ),
            ],
            database_operations=[],
        ),

        # Logement : id → id_logement (db_column='id', pas de SQL)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(
                    model_name='logement',
                    old_name='id',
                    new_name='id_logement',
                ),
                migrations.AlterField(
                    model_name='logement',
                    name='id_logement',
                    field=models.BigAutoField(primary_key=True, db_column='id', serialize=False),
                ),
            ],
            database_operations=[],
        ),
    ]
