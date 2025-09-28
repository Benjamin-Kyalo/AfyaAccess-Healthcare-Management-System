# pharmacy/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from billing.models import Billing


class Drug(models.Model):
    """
    Represents a drug/medicine in the pharmacy inventory.
    """
    AVAILABILITY_AVAILABLE = "Available"
    AVAILABILITY_OUT = "Out of stock"
    AVAILABILITY_CHOICES = [
        (AVAILABILITY_AVAILABLE, "Available"),
        (AVAILABILITY_OUT, "Out of stock"),
    ]

    name = models.CharField(max_length=255)
    strength_or_pack = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=0)  # safer than IntegerField
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default=AVAILABILITY_AVAILABLE
    )

    def __str__(self):
        return f"{self.name} ({self.strength_or_pack})"

    def ensure_availability(self):
        """
        Updates availability status based on quantity.
        """
        if self.quantity <= 0:
            self.availability_status = self.AVAILABILITY_OUT
        else:
            self.availability_status = self.AVAILABILITY_AVAILABLE
        # save only this field
        self.save(update_fields=["availability_status"])
        return self.availability_status


class Dispense(models.Model):
    """
    Represents a pharmacy dispense transaction for a prescription.
    """
    # Use string FK to avoid circular import at module load time
    prescription = models.ForeignKey('consultation.Prescription', on_delete=models.CASCADE, related_name="dispenses")
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Dispense #{self.id} for Prescription #{self.prescription_id}"


class DispenseLine(models.Model):
    """
    Each drug line in a dispense.
    """
    dispense = models.ForeignKey(Dispense, on_delete=models.CASCADE, related_name="lines")
    # link to consultation.PrescriptionItem by string
    prescription_item = models.ForeignKey('consultation.PrescriptionItem', on_delete=models.PROTECT)
    drug = models.ForeignKey(Drug, on_delete=models.PROTECT)
    quantity_dispensed = models.PositiveIntegerField()
    unit_price_at_dispense = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.drug.name} x {self.quantity_dispensed}"

    def save(self, *args, **kwargs):
        """
        Reduce stock when creating a new dispense line - transactional safety is enforced in the view.
        """
        if self.pk is None:  # only on create
            if self.drug.quantity < self.quantity_dispensed:
                raise ValueError(
                    f"Not enough stock for {self.drug.name}. Available: {self.drug.quantity}"
                )
            # reduce stock
            self.drug.quantity -= self.quantity_dispensed
            # update availability and persist both fields
            self.drug.ensure_availability()
            self.drug.save(update_fields=["quantity", "availability_status"])
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    ACTION_PRESCRIPTION_CREATED = "prescription_created"
    ACTION_DISPENSE_CONFIRMED = "dispense_confirmed"
    ACTION_CHOICES = [
        (ACTION_PRESCRIPTION_CREATED, "Prescription created"),
        (ACTION_DISPENSE_CONFIRMED, "Dispense confirmed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    action = models.CharField(max_length=64, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"


# Signal: auto-create billing on dispense
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Dispense)
def create_billing_for_dispense(sender, instance, created, **kwargs):
    if created:
        # sum of lines (quantity * unit price at dispense)
        total_amount = sum(
            [line.quantity_dispensed * line.unit_price_at_dispense for line in instance.lines.all()]
        )
        if total_amount > 0:
            # Billing.patient field expects a Patient FK in your Billing model,
            # but earlier you used patient_name sometimes. Here we try to link to actual patient object if it exists.
            patient_obj = None
            try:
                patient_obj = instance.prescription.consultation.patient
            except Exception:
                patient_obj = None

            Billing.objects.create(
                patient=patient_obj,
                amount=total_amount,
                # Keep description field optional in Billing model; if it doesn't exist, remove it (see below).
                # In your Billing model earlier, there was no `description` field — if so, this will raise an error.
                # If your Billing model has no description, remove the 'description' kwarg.
                is_paid=False,
            )
