from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alpages", "0089_constraints_situation_quartier_parcours"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="situationdexploitation",
            index=models.Index(
                fields=["unite_pastorale", "annee"],
                name="idx_situation_up_annee",
            ),
        ),
        migrations.AddIndex(
            model_name="quartierpasto",
            index=models.Index(
                fields=["situation_exploitation"],
                name="idx_quartier_situation",
            ),
        ),
        migrations.AddIndex(
            model_name="exploiter",
            index=models.Index(
                fields=["quartier", "date_debut"],
                name="idx_parcours_quart_date",
            ),
        ),
        migrations.AddIndex(
            model_name="exploiter",
            index=models.Index(
                fields=["cheptel", "date_debut"],
                name="idx_parcours_chept_date",
            ),
        ),
    ]