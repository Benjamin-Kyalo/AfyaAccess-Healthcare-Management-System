# Django ORM base class for models
from django.db import models
# To reference AUTH_USER_MODEL (custom user model safe)          
from django.conf import settings
# For timestamp defaults      
from django.utils import timezone     
# Link consultations to patients
from patients.models import Patient   


class Investigation(models.Model):
    # Example: lab tests, x-rays
    name = models.CharField(max_length=255)  
    price = models.DecimalField(max_digits=10, decimal_places=2)  # test cost

    # Availability choices
    AVAILABILITY_AVAILABLE = "Available"
    AVAILABILITY_OUT = "Out of stock"
    AVAILABILITY_CHOICES = [
        (AVAILABILITY_AVAILABLE, "Available"),
        (AVAILABILITY_OUT, "Out of stock"),
    ]
    availability_status = models.CharField(
        max_length=20, 
        choices=AVAILABILITY_CHOICES, 
        default=AVAILABILITY_AVAILABLE
    )

    def __str__(self):
        return self.name  # readable name in admin/console


class Diagnosis(models.Model):
    # Example: Malaria, Diabetes, etc.
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Consultation(models.Model):
    # Link consultation to patient
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,      # delete consultation if patient deleted
        related_name="consultations",  # reverse lookup: patient.consultations.all()
        null=True,
        blank=True
    )

    # Snapshot fields (stored strings to keep history intact)
    patient_name = models.CharField(max_length=255, blank=True)
    doctor_name = models.CharField(max_length=255, blank=True)

    complaints = models.TextField(blank=True)  # patient complaints
    history = models.TextField(blank=True)     # medical history

    vitals = models.JSONField(default=dict, blank=True)  
    # Example: {"sys":120,"dia":80,"pulse":72}

    # Many-to-many links
    investigations = models.ManyToManyField(Investigation, blank=True, related_name="consultations")
    diagnoses = models.ManyToManyField(Diagnosis, blank=True, related_name="consultations")

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Consultation #{self.id} for {self.patient}"


class Prescription(models.Model):
    # Status options for tracking
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
    Each item in a prescription.
    Links drug + dosage instructions + quantities.
    """

    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    drug = models.ForeignKey("pharmacy.Drug", on_delete=models.PROTECT)  # avoid delete if drug in use

    # Doctor’s request and pharmacy’s record
    quantity_requested = models.IntegerField()
    quantity_dispensed = models.IntegerField(default=0)

    # Route of administration (options)
    ROUTE_CHOICES = [
        ("oral", "Oral"),
        ("iv", "Intravenous"),
        ("im", "Intramuscular"),
        ("sc", "Subcutaneous"),
        ("topical", "Topical"),
        ("inhalation", "Inhalation"),
        ("sublingual", "Sublingual"),
    ]
    route = models.CharField(max_length=50, choices=ROUTE_CHOICES, blank=True)

    # Units (mg, ml, tablet, etc.)
    UNIT_CHOICES = [
        ("mg", "Milligram"),
        ("g", "Gram"),
        ("ml", "Milliliter"),
        ("tablet", "Tablet"),
        ("capsule", "Capsule"),
        ("drop", "Drop"),
        ("puff", "Puff"),
    ]
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES, blank=True)

    # Frequency of administration
    FREQUENCY_CHOICES = [
        ("od", "Once daily"),
        ("bd", "Twice daily"),
        ("tds", "Three times daily"),
        ("qid", "Four times daily"),
        ("q4h", "Every 4 hours"),
        ("q6h", "Every 6 hours"),
        ("stat", "Immediately (STAT)"),
    ]
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES, blank=True)

    # Numeric dose & duration
    dose = models.PositiveIntegerField(null=True, blank=True, help_text="Amount per administration")
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="Number of days")

    def __str__(self):
        # readable display, safe if some fields missing
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
        Approximate total units = dose × duration.
        If missing, fallback to quantity_requested.
        """
        if self.dose and self.duration:
            return self.dose * self.duration
        return self.quantity_requested
