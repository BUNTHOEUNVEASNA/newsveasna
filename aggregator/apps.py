from django.apps import AppConfig


class AggregatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aggregator'

    def ready(self):
        """Register admin when app is ready."""
        try:
            from .admin import register_admin
            register_admin()
        except Exception:
            # Ignore errors during app loading
            pass