# lab/apps.py
from django.apps import AppConfig

class LabConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lab"
    verbose_name = "Laboratory"

    def ready(self):
        # Import signals to register handlers (post_save for LabRequest).
        # Import inside ready() to avoid app-loading issues at import time.
        from . import signals  # noqa: F401
