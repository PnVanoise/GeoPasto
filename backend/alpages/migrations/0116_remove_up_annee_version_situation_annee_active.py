from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("alpages", "0115_geometrie_unite_pastorale"),
    ]

    operations = [
        # UnitePastorale
        migrations.RemoveField(model_name="unitepastorale", name="annee_version"),
        migrations.RemoveField(model_name="unitepastorale", name="version_active"),
        # SituationDExploitation — contrainte unique d'abord, puis champs
        migrations.RemoveConstraint(
            model_name="situationdexploitation",
            name="uniq_situation_up_annee",
        ),
        migrations.RemoveField(model_name="situationdexploitation", name="annee"),
        migrations.RemoveField(model_name="situationdexploitation", name="situation_active"),
    ]
