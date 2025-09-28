# consultation/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

from patients.models import Patient


class Investigation(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    AVAILABILITY_AVAILABLE = "Available"
    AVAILABILITY_OUT = "Out of stock"
    AVAILABILITY_CHOICES = [
        (AVAILABILITY_AVAILABLE, "Available"),
        (AVAILABILITY_OUT, "Out of stock"),
    ]
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default=AVAILABILITY_AVAILABLE)

    def __str__(self):
        return self.name


class Diagnosis(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Consultation(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="consultations",
        null=True,  # allow nulls for now
        blank=True
    )
    # snapshot fields (denormalized for quick access / historical record)
    patient_name = models.CharField(max_length=255, blank=True)
    doctor_name = models.CharField(max_length=255, blank=True)

    complaints = models.TextField(blank=True)
    history = models.TextField(blank=True)

    # Structured vitals stored as JSON
    vitals = models.JSONField(default=dict, blank=True)
    # Example: {"sys": 120, "dia": 80, "pulse": 72, "temp": 36.7, "rr": 18, "rbs": 110, "spo2": 98}

    investigations = models.ManyToManyField(Investigation, blank=True, related_name="consultations")
    diagnoses = models.ManyToManyField(Diagnosis, blank=True, related_name="consultations")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Consultation #{self.id} for {self.patient}"


class Prescription(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PARTIAL = "partial"
    STATUS_DISPENSED = "dispensed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PARTIAL, "Partial"),
        (STATUS_DISPENSED, "Dispensed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="prescriptions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Prescription #{self.id} ({self.status})"


class PrescriptionItem(models.Model):
    """
    Each line in a prescription — doctor selects drug from pharmacy catalog,
    selects route/unit/frequency from choices and provides numeric dose and duration.
    quantity_requested is the number of units the doctor requests (can be derived from dose/duration).
    quantity_dispensed is updated by pharmacy when dispensing.
    """

    # Keep the relation to Prescription
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")

    # Link to pharmacy Drug (string avoids import-time circular issues)
    drug = models.ForeignKey("pharmacy.Drug", on_delete=models.PROTECT)

    # requested / dispensed counters (unchanged semantics)
    quantity_requested = models.IntegerField()
    quantity_dispensed = models.IntegerField(default=0)

    # Dropdown choices (required by your request: at least 7 options)
    ROUTE_ORAL = "oral"
    ROUTE_IV = "iv"
    ROUTE_IM = "im"
    ROUTE_SC = "sc"
    ROUTE_TOPICAL = "topical"
    ROUTE_INHALATION = "inhalation"
    ROUTE_SUBLINGUAL = "sublingual"

    ROUTE_CHOICES = [
        (ROUTE_ORAL, "Oral"),
        (ROUTE_IV, "Intravenous"),
        (ROUTE_IM, "Intramuscular"),
        (ROUTE_SC, "Subcutaneous"),
        (ROUTE_TOPICAL, "Topical"),
        (ROUTE_INHALATION, "Inhalation"),
        (ROUTE_SUBLINGUAL, "Sublingual"),
    ]
    route = models.CharField(max_length=50, choices=ROUTE_CHOICES, blank=True)

    UNIT_MG = "mg"
    UNIT_G = "g"
    UNIT_ML = "ml"
    UNIT_TABLET = "tablet"
    UNIT_CAPSULE = "capsule"
    UNIT_DROP = "drop"
    UNIT_PUFF = "puff"

    UNIT_CHOICES = [
        (UNIT_MG, "Milligram"),
        (UNIT_G, "Gram"),
        (UNIT_ML, "Milliliter"),
        (UNIT_TABLET, "Tablet"),
        (UNIT_CAPSULE, "Capsule"),
        (UNIT_DROP, "Drop"),
        (UNIT_PUFF, "Puff"),
    ]
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES, blank=True)

    FREQ_OD = "od"
    FREQ_BD = "bd"
    FREQ_TDS = "tds"
    FREQ_QID = "qid"
    FREQ_Q4H = "q4h"
    FREQ_Q6H = "q6h"
    FREQ_STAT = "stat"

    FREQUENCY_CHOICES = [
        (FREQ_OD, "Once daily"),
        (FREQ_BD, "Twice daily"),
        (FREQ_TDS, "Three times daily"),
        (FREQ_QID, "Four times daily"),
        (FREQ_Q4H, "Every 4 hours"),
        (FREQ_Q6H, "Every 6 hours"),
        (FREQ_STAT, "Immediately (STAT)"),
    ]
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES, blank=True)

    # Numeric fields (doctor must provide numeric dose and duration)
    dose = models.PositiveIntegerField(null=True, blank=True, help_text="Amount per administration (numeric)")
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="Number of days (numeric)")

    def __str__(self):
        # human readable summary; safe if some fields empty
        parts = [self.drug.name if self.drug_id else "Drug"]
        if self.dose:
            parts.append(f"{self.dose}{self.unit or ''}")
        if self.frequency:
            parts.append(f"({self.get_frequency_display()})")
        if self.duration:
            parts.append(f"for {self.duration}d")
        return " ".join(parts)

    @property
    def estimated_total_units(self):
        """
        Helpful helper: approximate total units needed based on dose and duration.
        (This is a simple helper — real calculation might depend on frequency mapping).
        Here we return dose * duration as you requested to help calculate billing.
        If dose or duration missing, fallback to quantity_requested.
        """
        if self.dose and self.duration:
            return self.dose * self.duration
        return self.quantity_requested
