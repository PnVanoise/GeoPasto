from django.apps import AppConfig


class SuiviPastoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "suivi_pasto"

    def ready(self):
        import suivi_pasto.audit_registry  # noqa: F401
