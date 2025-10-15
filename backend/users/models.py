from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    # We'll use Django Groups for permissioning.
    DESIGNATION_CHOICES = [
        ("doctor", "Medical Doctor / Physician"),
        ("nurse", "Registered Nurse"),
        ("pharmacist", "Pharmacist"),
        ("lab", "Clinical Lab Scientist"),
        ("reception", "Receptionist"),
        ("admin", "Hospital Administrator"),
    ]
    DEPARTMENT_CHOICES = [
        ("cardiology", "Cardiology"),
        ("pediatrics", "Pediatrics"),
        ("pharmacy", "Pharmacy"),
        ("lab", "Laboratory"),
        ("general", "General Medicine"),
        ("admin", "Administration"),
    ]

    designation = models.CharField(
        max_length=50,
        choices=DESIGNATION_CHOICES,
        null=True,
        blank=True,
        help_text="Select a designation (Doctor, Nurse, Pharmacist, etc.)",
    )

    # Contact details helpful for notifications and user lookup.
    phone_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Enter phone number e.g. +254712345678",
    )

    department = models.CharField(
        max_length=120,
        choices=DEPARTMENT_CHOICES,
        blank=True,
        null=True,
        help_text="Select the department this staff belongs to.",
    )

    # Audit timestamps — useful for tracing and reports.
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Friendly representation used in admin and logs.
        name = self.get_full_name() or self.username
        return f"{name} ({self.designation or 'No role'})"
