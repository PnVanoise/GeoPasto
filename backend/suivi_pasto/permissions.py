from rest_framework.permissions import DjangoModelPermissions


class StrictDjangoModelPermissions(DjangoModelPermissions):
    """
    DjangoModelPermissions étendu : GET requiert aussi view_*.

    DRF standard laisse passer GET pour tout utilisateur authentifié.
    Cette classe aligne le backend avec le frontend (can('view') requis pour lire).
    """

    perms_map = {
        **DjangoModelPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
    }
