from django.db import models
from django.conf import settings
# Link each bill to a patient
from patients.models import Patient  
# For calculating totals 
from django.db.models import Sum      

# Default service prices (KES)
SERVICE_DEFAULT_AMOUNTS = {
    "consultation": 1000,
    "laboratory": 1200,
    "imaging": 3000,
    "pharmacy": 2500,
    "minor_procedure": 3000,
    "surgery": 100000,
    "admission": 8000,
    "maternity": 70000,
    "physiotherapy": 2000,
    "specialist_consultation": 4000,
}

# Custom queryset for reusable billing queries
class BillingQuerySet(models.QuerySet):
    # Total amount of paid bills
    def paid_total(self):
        return self.filter(is_paid=True).aggregate(total=Sum("amount"))["total"] or 0

    # Total amount of unpaid bills
    def unpaid_total(self):
        return self.filter(is_paid=False).aggregate(total=Sum("amount"))["total"] or 0

    # Search bills by patient name or ID
    def by_patient_name_or_id(self, search_term):
        return self.filter(
            models.Q(patient__first_name__icontains=search_term) |
            models.Q(patient__last_name__icontains=search_term) |
            models.Q(patient__id__icontains=search_term)
        )

# Custom manager to expose custom queryset methods
class BillingManager(models.Manager):
    def get_queryset(self):
        return BillingQuerySet(self.model, using=self._db)

    def paid_total(self):
        return self.get_queryset().paid_total()

    def unpaid_total(self):
        return self.get_queryset().unpaid_total()

    def by_patient_name_or_id(self, search_term):
        return self.get_queryset().by_patient_name_or_id(search_term)

# Billing model for recording charges
class Billing(models.Model):
    # Link bill to patient
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,   # Delete bills if patient is deleted
        related_name="billings",
        null=True,
        blank=True,
    )
    # Store patient name for quick access
    patient_name = models.CharField(max_length=200, null=True, blank=True)

    # Type of service billed
    service = models.CharField(
        max_length=100,
        choices=[(k, k.replace("_", " ").title()) for k in SERVICE_DEFAULT_AMOUNTS.keys()],
        null=True,
        blank=True,
        default="consultation",
    )
    # Service amount
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # Payment status
    is_paid = models.BooleanField(default=False)

    # User who charged the bill
    charged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,   # Keep bill even if user is deleted
        null=True,
        blank=True,
        related_name="charges",
    )
    # Store name of charging user
    charged_by_name = models.CharField(max_length=200, null=True, blank=True)
    # Timestamp of when bill was created
    charged_at = models.DateTimeField(auto_now_add=True)

    # Use custom manager
    objects = BillingManager()

    # Override save method for auto-fill
    def save(self, *args, **kwargs):
        # Automatically set amount based on service
        if self.service in SERVICE_DEFAULT_AMOUNTS:
            self.amount = SERVICE_DEFAULT_AMOUNTS[self.service]
        # Store patient name automatically
        if self.patient:
            self.patient_name = f"{self.patient.first_name} {self.patient.last_name}".strip()
        # Store charged_by name automatically
        if self.charged_by:
            self.charged_by_name = self.charged_by.get_full_name() or self.charged_by.username
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_name or 'Unknown'} - {self.service} ({self.amount} KES)"
