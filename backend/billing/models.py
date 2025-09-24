from django.db import models
from django.conf import settings
from patients.models import Patient
from django.db.models import Sum

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

class BillingQuerySet(models.QuerySet):
    def paid_total(self):
        return self.filter(is_paid=True).aggregate(total=Sum("amount"))["total"] or 0

    def unpaid_total(self):
        return self.filter(is_paid=False).aggregate(total=Sum("amount"))["total"] or 0

    def by_patient_name_or_id(self, search_term):
        return self.filter(
            models.Q(patient__first_name__icontains=search_term) |
            models.Q(patient__last_name__icontains=search_term) |
            models.Q(patient__id__icontains=search_term)
        )

class BillingManager(models.Manager):
    def get_queryset(self):
        return BillingQuerySet(self.model, using=self._db)

    # Optional: also expose these methods directly on manager
    def paid_total(self):
        return self.get_queryset().paid_total()

    def unpaid_total(self):
        return self.get_queryset().unpaid_total()

    def by_patient_name_or_id(self, search_term):
        return self.get_queryset().by_patient_name_or_id(search_term)

class Billing(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="billings",
        null=True,
        blank=True,
    )
    patient_name = models.CharField(max_length=200, null=True, blank=True)

    service = models.CharField(
        max_length=100,
        choices=[(k, k.replace("_", " ").title()) for k in SERVICE_DEFAULT_AMOUNTS.keys()],
        null=True,
        blank=True,
        default="consultation",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)

    charged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="charges",
    )
    charged_by_name = models.CharField(max_length=200, null=True, blank=True)
    charged_at = models.DateTimeField(auto_now_add=True)

    objects = BillingManager()  # use the custom manager

    def save(self, *args, **kwargs):
        if self.service in SERVICE_DEFAULT_AMOUNTS:
            self.amount = SERVICE_DEFAULT_AMOUNTS[self.service]
        if self.patient:
            self.patient_name = f"{self.patient.first_name} {self.patient.last_name}".strip()
        if self.charged_by:
            self.charged_by_name = self.charged_by.get_full_name() or self.charged_by.username
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_name or 'Unknown'} - {self.service} ({self.amount} KES)"
