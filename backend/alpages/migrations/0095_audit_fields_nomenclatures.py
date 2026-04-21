from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alpages", "0094_exploiter_nombre_animaux"),
    ]

    operations = [
        migrations.AlterField(
            model_name="abridurgence",
            name="created_by",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name="abridurgence",
            name="created_on",
            field=models.DateTimeField(auto_now_add=True, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="abridurgence",
            name="modified_by",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name="abridurgence",
            name="modified_on",
            field=models.DateTimeField(auto_now=True, blank=True, null=True),
        ),
        migrations.AddField(
            model_name="typeequipement",
            name="created_by",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="typeequipement",
            name="created_on",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="typeequipement",
            name="modified_by",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="typeequipement",
            name="modified_on",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name="typeevenement",
            name="created_by",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="typeevenement",
            name="created_on",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="typeevenement",
            name="modified_by",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="typeevenement",
            name="modified_on",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
