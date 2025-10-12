# billing/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Payment

@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    """Ensure billing status refresh after payment save (safe duplicate call)."""
    try:
        instance.billing.refresh_status_from_payments()
    except Exception:
        pass

@receiver(post_delete, sender=Payment)
def payment_post_delete(sender, instance, **kwargs):
    """Ensure billing status refresh after payment deletion."""
    try:
        instance.billing.refresh_status_from_payments()
    except Exception:
        pass
