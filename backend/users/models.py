from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    DESIGNATION_CHOICES = [
        ("doctor", "Medical Doctor / Physician"),
        ("nurse", "Registered Nurse"),
        ("surgeon", "Surgeon"),
        ("anesthetist", "Anesthesiologist / Nurse Anesthetist"),
        ("pharmacist", "Pharmacist"),
        ("lab", "Clinical Lab Scientist"),
        ("radiographer", "Radiographer"),
        ("physiotherapist", "Physiotherapist"),
        ("midwife", "Midwife / Obstetric Nurse"),
        ("admin", "Hospital Administrator"),
    ]
    designation = models.CharField(
        max_length=50, choices=DESIGNATION_CHOICES, null=True, blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.designation or 'No role'})"
