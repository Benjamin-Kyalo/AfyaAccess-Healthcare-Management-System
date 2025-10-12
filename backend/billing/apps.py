# billing/apps.py
from django.apps import AppConfig

class BillingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "billing"

    def ready(self):
        # Import signals to ensure they are registered (no-op if not present)
        try:
            import billing.signals  # noqa: F401
        except Exception:
            # Avoid crashing if signals file not present during initial migrations
            pass
