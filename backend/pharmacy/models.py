from django.db import models
from django.conf import settings
from django.utils import timezone
from billing.models import Billing

class Drug(models.Model):
    """Represents a drug/medicine in the pharmacy inventory."""

    # Availability options
    AVAILABILITY_AVAILABLE = "Available"
    AVAILABILITY_OUT = "Out of stock"
    AVAILABILITY_CHOICES = [
        (AVAILABILITY_AVAILABLE, "Available"),
        (AVAILABILITY_OUT, "Out of stock"),
    ]

    # Drug details
    name = models.CharField(max_length=255)  # drug name
    strength_or_pack = models.CharField(max_length=255, blank=True)  # dosage or pack size
    quantity = models.PositiveIntegerField(default=0)  # stock count, must be ≥0
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # cost per unit
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default=AVAILABILITY_AVAILABLE
    )

    def __str__(self):
        return f"{self.name} ({self.strength_or_pack})"

    def ensure_availability(self):
        """
        Updates availability status depending on stock quantity.
        """
        if self.quantity <= 0:
            self.availability_status = self.AVAILABILITY_OUT
        else:
            self.availability_status = self.AVAILABILITY_AVAILABLE
        # Save only the availability field to DB
        self.save(update_fields=["availability_status"])
        return self.availability_status


class Dispense(models.Model):
    """Represents a pharmacy dispense transaction for a prescription."""

    # Prescription link (string import to avoid circular imports)
    prescription = models.ForeignKey(
        'consultation.Prescription',
        on_delete=models.CASCADE,
        related_name="dispenses"
    )
    # Who performed the dispensing
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    # When the dispense happened
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Dispense #{self.id} for Prescription #{self.prescription_id}"


class DispenseLine(models.Model):
    """Each drug line item inside a dispense."""

    dispense = models.ForeignKey(
        Dispense, on_delete=models.CASCADE, related_name="lines"
    )
    # Which prescription item was dispensed
    prescription_item = models.ForeignKey(
        'consultation.PrescriptionItem', on_delete=models.PROTECT
    )
    # Which drug was given
    drug = models.ForeignKey(Drug, on_delete=models.PROTECT)
    quantity_dispensed = models.PositiveIntegerField()  # units given to patient
    unit_price_at_dispense = models.DecimalField(max_digits=10, decimal_places=2)  # price recorded at time of dispense

    def __str__(self):
        return f"{self.drug.name} x {self.quantity_dispensed}"

    def save(self, *args, **kwargs):
        """
        Reduce stock only when creating a new dispense line.
        """
        if self.pk is None:  # run only on create
            if self.drug.quantity < self.quantity_dispensed:
                raise ValueError(
                    f"Not enough stock for {self.drug.name}. Available: {self.drug.quantity}"
                )
            # Deduct stock
            self.drug.quantity -= self.quantity_dispensed
            # Update availability status
            self.drug.ensure_availability()
            # Save updated stock and status
            self.drug.save(update_fields=["quantity", "availability_status"])
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    """Logs important pharmacy actions for accountability."""

    # Possible actions
    ACTION_PRESCRIPTION_CREATED = "prescription_created"
    ACTION_DISPENSE_CONFIRMED = "dispense_confirmed"
    ACTION_CHOICES = [
        (ACTION_PRESCRIPTION_CREATED, "Prescription created"),
        (ACTION_DISPENSE_CONFIRMED, "Dispense confirmed"),
    ]

    # Who did the action
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    action = models.CharField(max_length=64, choices=ACTION_CHOICES)  # type of action
    timestamp = models.DateTimeField(auto_now_add=True)  # when it happened
    details = models.JSONField(default=dict)  # extra info in JSON format

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"


# --- Signals: create a Billing record automatically when a Dispense is saved ---

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Dispense)
def create_billing_for_dispense(sender, instance, created, **kwargs):
    """When a dispense is created, auto-generate a billing record."""
    if created:
        # Calculate total amount = sum of each line’s cost
        total_amount = sum(
            [line.quantity_dispensed * line.unit_price_at_dispense for line in instance.lines.all()]
        )
        if total_amount > 0:
            # Try to attach patient if linked
            patient_obj = None
            try:
                patient_obj = instance.prescription.consultation.patient
            except Exception:
                patient_obj = None

            # Create billing record
            Billing.objects.create(
                patient=patient_obj,
                amount=total_amount,
                is_paid=False,
            )
