from django.contrib.auth.models import AbstractUser
from django.db import models

# Custom User model extending Django's built-in AbstractUser
class User(AbstractUser):
    # Possible staff roles in the hospital
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

    # Field to store user’s professional designation
    designation = models.CharField(
        max_length=50, choices=DESIGNATION_CHOICES, null=True, blank=True
    )

    def __str__(self):
        # Display username and designation (or "No role" if missing)
        return f"{self.username} ({self.designation or 'No role'})"
