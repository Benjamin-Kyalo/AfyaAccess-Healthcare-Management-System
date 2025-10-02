# This file defines configuration for the lab application.
from django.apps import AppConfig
class LabConfig(AppConfig):
    # Use BigAutoField for primary keys by default
    default_auto_field = "django.db.models.BigAutoField"
    # Name of the app (must match folder name)
    name = "lab"
    # Human-readable name for the admin site
    verbose_name = "Laboratory"

    def ready(self):
        """
        This method is called when Django starts.
        We import signals here so that post_save hooks for LabRequest
        (e.g., creating a billing record automatically) are registered.
        Importing inside ready() avoids circular imports or premature loading issues.
        """
        from . import signals  # noqa: F401  # The noqa ignores unused import warning
