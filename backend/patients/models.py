# patients/models.py
from django.db import models
from django.conf import settings

class Patient(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("intersex", "Intersex"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("registered", "Registered"),
        ("sent_to_billing", "Sent to Billing"),
        ("ready_for_doctor", "Ready for Doctor"),
        ("lab_requested", "Lab Requested"),
        ("xray_requested", "X-ray Requested"),
        ("prescribed", "Prescribed"),
        ("dispensed", "Dispensed"),
    ]

    first_name = models.CharField(max_length=100, null=True, blank=True, default="Unknown")
    last_name = models.CharField(max_length=100, null=True, blank=True, default="Unknown")
    age = models.IntegerField(null=True, blank=True, default=0)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="other")
    national_id = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)

    # system-controlled status
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="registered", editable=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name", "national_id", "phone"],
                name="unique_patient_record"
            )
        ]

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()


class PatientStatusHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="status_history")
    old_status = models.CharField(max_length=50, null=True, blank=True)
    new_status = models.CharField(max_length=50, null=True, blank=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    note = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.patient} : {self.old_status} -> {self.new_status} @ {self.timestamp}"
