# lab/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LabRequest
from billing.models import Billing

# Signal: when a LabRequest is created, auto-create a Billing entry
@receiver(post_save, sender=LabRequest)
def create_billing_for_lab_request(sender, instance, created, **kwargs):
    if created:
        # Decide test name
        if instance.test_name:
            test_name = instance.test_name
        elif instance.investigation:
            test_name = str(instance.investigation)
        else:
            test_name = "Unknown Test"

        # Build billing service string
        service_name = f"Lab Test: {test_name} (request_id={instance.id})"

        # Create billing only if not already existing
        Billing.objects.get_or_create(
            patient=instance.patient,
            service=service_name,
            defaults={
                "amount": instance.get_price(),
                "is_paid": False,
            },
        )
