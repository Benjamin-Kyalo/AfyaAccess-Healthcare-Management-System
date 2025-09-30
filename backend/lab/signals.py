# lab/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LabRequest
from billing.models import Billing

@receiver(post_save, sender=LabRequest)
def create_billing_for_lab_request(sender, instance, created, **kwargs):
    if created:
        from billing.models import Billing

        # Use test_name if present, otherwise fall back to investigation
        if hasattr(instance, "test_name") and instance.test_name:
            test_name = instance.test_name
        elif hasattr(instance, "investigation") and instance.investigation:
            test_name = str(instance.investigation)
        else:
            test_name = "Unknown Test"

        # Build the service string (matches serializer convention)
        service_name = f"Lab Test: {test_name} (request_id={instance.id})"

        # Only create billing if it doesn’t already exist
        Billing.objects.get_or_create(
            patient=instance.patient,
            service=service_name,
            defaults={
                "amount": instance.get_price(),
                "is_paid": False,
            },
        )
