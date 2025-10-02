"""
Patients models: add canonical patient_number, created_by, status and helper.
- patient_number is generated after initial save using the DB-assigned id (PAT-0000001).
- Fields are nullable/blank to avoid migration issues for existing installs.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone

GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("intersex", "Intersex"),
        ("other", "Other"),
    ]

class Patient(models.Model):
    # Basic demographics (assume these already existed — keep them).
    first_name = models.CharField(max_length=100, null=True, blank=True, default="Unknown")
    last_name = models.CharField(max_length=100, null=True, blank=True, default="Unknown")
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, default="other")
    dob = models.DateField(blank=True, null=True, help_text="Date of birth")
    national_id = models.CharField(max_length=50, blank=True, null=True, unique=False)
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Enter phone number e.g. +254712345678",
    )
   
    # Canonical patient identifier: set after first save using ID to avoid concurrency.
    patient_number = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
        help_text="Auto-generated unique patient number (e.g. PAT-0000123)."
    )
    address = models.TextField(blank=True, null=True)
    # Who created this patient record (nullable to remain safe)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patients_created",
        help_text="User who registered the patient (if known).",
    )

    # Simple status lifecycle for workflows
    STATUS_CHOICES = [
        ("registered", "Registered"),
        ("triaged", "Triaged"),
        ("waiting_for_doctor", "Waiting for Doctor"),
        ("in_consultation", "In Consultation"),
        ("ready_for_pharmacy", "Ready for Pharmacy"),
        ("discharged", "Discharged"),
    ]
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="registered")

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Optional last visit date, helpful in reports
    last_visit = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient_number or 'NEW'} — {self.first_name} {self.last_name or ''}"

    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()
    
class PatientStatusHistory(models.Model):
    """
    Stores a history of status changes for auditing.
    Each time a patient's status changes, create a row here.
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="status_history")
    old_status = models.CharField(max_length=32, blank=True, null=True)
    new_status = models.CharField(max_length=32)  # increased from previous shorter length
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="status_changes"
    )

    def __str__(self):
        return f"{self.patient.patient_number} {self.old_status} → {self.new_status} at {self.changed_at:%Y-%m-%d %H:%M}"


# Post-save handler to generate patient_number using DB id (avoids race conditions)
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Patient)
def ensure_patient_number(sender, instance: Patient, created, **kwargs):
    """
    Ensure patient_number is set after initial save.
    Uses the instance.pk (DB id) to create predictable unique number:
    PAT-<id:07d> e.g. PAT-0000123
    This is safe because pk is assigned on first save.
    """
    if created and not instance.patient_number:
        # Compose patient number using the DB id
        instance.patient_number = f"PAT-{instance.pk:07d}"
        # Avoid recursion by updating only the patient_number field
        Patient.objects.filter(pk=instance.pk).update(patient_number=instance.patient_number)
