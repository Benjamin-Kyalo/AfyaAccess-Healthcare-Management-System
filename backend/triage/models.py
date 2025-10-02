from django.db import models
from django.conf import settings
from patients.models import Patient

class TriageRecord(models.Model):
    """
    Stores a single triage record (vital signs) for a patient.
    Links to the patient and the attending user (staff).
    """
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="triage_records"
    )
    attended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attended_triages"
    )

    # Vital signs with defaults
    temperature_c = models.FloatField(default=0.0, help_text="Temperature in °C")
    heart_rate_bpm = models.PositiveIntegerField(default=0, help_text="Heart rate in beats per minute")
    respiratory_rate_bpm = models.PositiveIntegerField(default=0, help_text="Respiratory rate in bpm")
    systolic_bp = models.IntegerField(default=0, help_text="Systolic BP in mmHg")
    diastolic_bp = models.IntegerField(default=0, help_text="Diastolic BP in mmHg")
    spo2_percent = models.FloatField(default=0.0, help_text="Oxygen saturation in %")
    weight_kg = models.FloatField(default=0.0, help_text="Weight in kg")
    height_cm = models.FloatField(default=0.0, help_text="Height in cm")
    bmi = models.FloatField(help_text="BMI kg/m²", null=True, blank=True)

    # Auto fields
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_bmi(self):
        """Utility: calculate BMI from weight and height."""
        if self.height_cm > 0:
            return round(self.weight_kg / ((self.height_cm / 100) ** 2), 2)
        return None

    def save(self, *args, **kwargs):
        # Auto-calculate BMI before saving
        self.bmi = self.calculate_bmi()
        super().save(*args, **kwargs)

    def __str__(self):
        # Readable string in admin/UI.
        return f"Triage for {self.patient} by {self.attended_by.username if self.attended_by else 'Unknown'}"