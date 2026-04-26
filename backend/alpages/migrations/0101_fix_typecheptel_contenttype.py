from django.db import migrations


def rename_typecheptel_contenttype(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')

    # Supprimer le content type orphelin (ancien modèle supprimé en 0085)
    orphan = ContentType.objects.filter(app_label='alpages', model='typecheptel').first()
    if orphan:
        Permission.objects.filter(content_type=orphan).delete()
        orphan.delete()

    # Renommer les codenames de permissions type_cheptel → typecheptel
    current = ContentType.objects.filter(app_label='alpages', model='type_cheptel').first()
    if current:
        for perm in Permission.objects.filter(content_type=current):
            perm.codename = perm.codename.replace('type_cheptel', 'typecheptel')
            perm.save()
        current.model = 'typecheptel'
        current.save()


class Migration(migrations.Migration):

    dependencies = [
        ('alpages', '0100_rename_snake_case_models_to_camelcase'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(
            rename_typecheptel_contenttype,
            migrations.RunPython.noop,
        ),
    ]
