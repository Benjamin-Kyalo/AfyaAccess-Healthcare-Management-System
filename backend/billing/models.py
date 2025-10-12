from decimal import Decimal
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.core.validators import MinValueValidator

# Keep your original default service prices mapping (KES)
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
    """Custom queryset with helpful aggregation helpers used by reports/views."""

    def paid_total(self):
        """Sum of amounts for bills with status == paid (Decimal)."""
        total = self.filter(status=Billing.STATUS_PAID).aggregate(total=Sum("amount"))["total"]
        return total or Decimal("0.00")

    def unpaid_total(self):
        """Sum for bills that are not paid (pending or partial)."""
        total = self.exclude(status=Billing.STATUS_PAID).aggregate(total=Sum("amount"))["total"]
        return total or Decimal("0.00")

    def cancelled_total(self):
        """Sum for bills that are cancelled (useful in reports)."""
        total = self.filter(status=Billing.STATUS_CANCELLED).aggregate(total=Sum("amount"))["total"]
        return total or Decimal("0.00")

    def total_by_service(self):
        """Return totals grouped by service (list of dicts when evaluated)."""
        return self.values("service").annotate(total=Sum("amount")).order_by("-total")

    def by_patient_name_or_id(self, search_term):
        """Search helper by patient fields or cached patient_name (keeps search flexible)."""
        return self.filter(
            models.Q(patient__first_name__icontains=search_term)
            | models.Q(patient__last_name__icontains=search_term)
            | models.Q(patient__id__icontains=search_term)
            | models.Q(patient_name__icontains=search_term)
        )

    def total_for_patient(self, patient_id):
        """
        Convenience: total expected billing amount for a given patient (sums all bills).
        Returns Decimal.
        """
        total = self.filter(patient__id=patient_id).aggregate(total=Sum("amount"))["total"]
        return total or Decimal("0.00")


class BillingManager(models.Manager):
    """Expose BillingQuerySet helpers on Billing.objects."""

    def get_queryset(self):
        return BillingQuerySet(self.model, using=self._db)

    def paid_total(self):
        return self.get_queryset().paid_total()

    def unpaid_total(self):
        return self.get_queryset().unpaid_total()

    def cancelled_total(self):
        return self.get_queryset().cancelled_total()

    def total_by_service(self):
        return self.get_queryset().total_by_service()

    def by_patient_name_or_id(self, term):
        return self.get_queryset().by_patient_name_or_id(term)

    def total_for_patient(self, patient_id):
        return self.get_queryset().total_for_patient(patient_id)


class Billing(models.Model):
    """
    Billing record representing a single service charge.
    - Keeps your original fields and behavior, extended with invoice/status/links.
    """

    # Link to patient model (string used to avoid circular imports)
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="billings",
        null=True,
        blank=True,
        help_text="Patient this billing belongs to",
    )

    # Cache patient name for display and quick search
    patient_name = models.CharField(max_length=200, null=True, blank=True)

    # Service type (keeps original choices and defaults)
    service = models.CharField(
        max_length=100,
        choices=[(k, k.replace("_", " ").title()) for k in SERVICE_DEFAULT_AMOUNTS.keys()],
        null=True,
        blank=True,
        default="consultation",
        help_text="Service charged (used to derive default price)",
    )

    # Amount as Decimal to avoid float precision problems
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Total amount charged for this billing record",
    )

    # Currency code (default KES)
    currency = models.CharField(max_length=6, default="KES", help_text="Currency code (e.g., KES)")

    # Legacy boolean preserved for backward compatibility (kept in sync with `status`)
    is_paid = models.BooleanField(default=False, help_text="Legacy boolean derived from status")

    # Who recorded the billing (preserved existing field)
    charged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="charges",
        help_text="User who created the billing record",
    )
    charged_by_name = models.CharField(max_length=200, null=True, blank=True)

    # Original timestamp preserved for compatibility
    charged_at = models.DateTimeField(auto_now_add=True)

    # Additional audit timestamps
    created_at = models.DateTimeField(default=timezone.now, help_text="Record created timestamp")
    updated_at = models.DateTimeField(auto_now=True, help_text="Record last updated timestamp")

    # Human-friendly invoice number, unique. Auto-generated when missing.
    invoice_number = models.CharField(max_length=64, unique=True, blank=True, null=True, help_text="Invoice id like INV-AA-YYYYMMDD-XXXXXX")

    # Status lifecycle values and choices
    STATUS_PENDING = "pending"
    STATUS_PARTIAL = "partial"
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_PARTIAL, "Partially Paid"),
        (STATUS_PAID, "Paid"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING, help_text="Payment status")

    # Optional explicit links to lab and pharmacy models (keeps integrations clean)
    lab_request = models.ForeignKey(
        "lab.LabRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billings",
        help_text="Link to lab request that generated this bill",
    )
    dispense = models.ForeignKey(
        "pharmacy.Dispense",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billings",
        help_text="Link to pharmacy dispense that generated this bill",
    )

    # Optional external reference or notes (e.g., cancellation reason appended)
    report_reference = models.CharField(max_length=256, null=True, blank=True, help_text="External reference or notes")

    # Custom manager
    objects = BillingManager()

    class Meta:
        indexes = [
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["patient"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["-created_at"]
        verbose_name = "Billing"
        verbose_name_plural = "Billings"

    def __str__(self):
        return f"{self.invoice_number or self.pk} - {self.patient_name or 'Unknown'} - {self.amount} {self.currency}"

    # -------------------------
    # Internal helpers
    # -------------------------
    def _generate_invoice_number(self):
        """
        Generate invoice string with project initials 'AA':
        format: INV-AA-YYYYMMDD-XXXXXX
        """
        date_str = timezone.now().strftime("%Y%m%d")
        short_token = uuid.uuid4().hex[:6].upper()
        return f"INV-AA-{date_str}-{short_token}"

    def save(self, *args, **kwargs):
        """
        Save hook:
        - Preserve original defaulting for amount from SERVICE_DEFAULT_AMOUNTS.
        - Auto-fill cached patient_name and charged_by_name.
        - Auto-generate invoice_number if missing.
        - Sync is_paid boolean to match status.
        - Ensure amount is Decimal.
        """
        # Apply default amount from mapping when applicable (original flow)
        if self.service in SERVICE_DEFAULT_AMOUNTS:
            self.amount = Decimal(str(SERVICE_DEFAULT_AMOUNTS[self.service]))

        # Cache patient name to avoid extra joins
        if self.patient:
            self.patient_name = f"{self.patient.first_name} {self.patient.last_name}".strip()

        # Cache charged_by_name if user provided
        if self.charged_by:
            self.charged_by_name = self.charged_by.get_full_name() or getattr(self.charged_by, "username", "")

        # Generate invoice if missing
        if not self.invoice_number:
            self.invoice_number = self._generate_invoice_number()

        # Keep legacy boolean in sync with status
        self.is_paid = True if self.status == self.STATUS_PAID else False

        # Defensive ensure Decimal
        if not isinstance(self.amount, Decimal):
            try:
                self.amount = Decimal(str(self.amount))
            except Exception:
                self.amount = Decimal("0.00")

        super().save(*args, **kwargs)

    # -------------------------
    # Payment-related helpers
    # -------------------------
    def payments_qs(self):
        """Convenience wrapper returning related payments queryset (related_name='payments')."""
        return self.payments.all()

    def total_paid_amount(self):
        """Return Decimal sum of all payments applied to this billing record."""
        total = self.payments.aggregate(total=Sum("amount"))["total"]
        return total or Decimal("0.00")

    def calculate_balance(self):
        """Return outstanding balance (never negative)."""
        paid = self.total_paid_amount()
        balance = (self.amount - paid) if self.amount > paid else Decimal("0.00")
        return balance

    def refresh_status_from_payments(self):
        """
        Recompute and persist the status based on payments:
        - 0 paid -> pending
        - 0 < paid < amount -> partial
        - paid >= amount -> paid
        Only persists when status changes (reduces DB write churn).
        """
        paid = self.total_paid_amount()
        new_status = self.STATUS_PENDING
        if paid == Decimal("0.00"):
            new_status = self.STATUS_PENDING
        elif paid < self.amount:
            new_status = self.STATUS_PARTIAL
        else:
            new_status = self.STATUS_PAID

        if new_status != self.status:
            # Save only status (and updated_at auto-updates). save() syncs is_paid
            self.status = new_status
            self.save(update_fields=["status", "updated_at"])

    def create_payment(self, amount, method="cash", reference=None, user=None):
        """
        Create a Payment record for this billing, then refresh status.
        - Validates positive amount.
        - Returns the created Payment instance.
        """
        from .models import Payment  # local import to avoid circular import issues

        try:
            amount_dec = Decimal(str(amount))
        except Exception:
            raise ValueError("Invalid amount format for payment")

        if amount_dec <= Decimal("0.00"):
            raise ValueError("Payment amount must be positive")

        payment = Payment.objects.create(
            billing=self,
            amount=amount_dec,
            payment_method=method,
            reference_number=reference,
            created_by=user,
        )
        # Recompute status after creating a payment
        self.refresh_status_from_payments()
        return payment

    def cancel(self, reason=None, user=None):
        """
        Cancel this bill:
        - Set status to CANCELLED
        - Append cancel reason to report_reference with timestamp (keeps audit)
        - Keep payments for audit (do not delete)
        """
        self.status = self.STATUS_CANCELLED
        if reason:
            prev = self.report_reference or ""
            timestamp = timezone.now().isoformat()
            self.report_reference = f"{prev} CANCELLED[{timestamp}]:{reason}"
        if user and not self.charged_by:
            self.charged_by = user
            self.charged_by_name = user.get_full_name() or getattr(user, "username", "")
        self.save()
        return self


class Payment(models.Model):
    """
    Payment ledger entry linked to Billing.

    - amount: Decimal
    - payment_method: e.g., cash, mpesa, insurance
    - reference_number: external txn id
    - created_by: which staff recorded the payment
    - created_at: timestamp
    """

    PAYMENT_METHODS = (
        ("cash", "Cash"),
        ("mpesa", "M-Pesa"),
        ("insurance", "Insurance"),
        ("card", "Card"),
        ("bank_transfer", "Bank Transfer"),
        ("other", "Other"),
    )

    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name="payments", help_text="Billing this payment applies to")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Amount paid",
    )
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default="cash", help_text="Payment method")
    reference_number = models.CharField(max_length=128, null=True, blank=True, help_text="Gateway/receipt reference")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who recorded payment")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment {self.pk} - {self.amount} ({self.payment_method})"

    def save(self, *args, **kwargs):
        """
        Save the Payment and then refresh the parent Billing's status.
        We call super() first so the payment exists in DB when aggregates run.
        """
        super().save(*args, **kwargs)
        try:
            self.billing.refresh_status_from_payments()
        except Exception:
            # Defensive: payment creation should not fail because status refresh fails
            pass

    def delete(self, *args, **kwargs):
        """
        When a payment is deleted (refund/mistake), refresh billing status afterwards.
        """
        billing = self.billing
        super().delete(*args, **kwargs)
        try:
            billing.refresh_status_from_payments()
        except Exception:
            pass
