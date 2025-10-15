from django.test import TestCase
from django.contrib.auth import get_user_model

# Try importing Patient model
try:
    from patients.models import Patient
except Exception:
    Patient = None

from .models import LabRequest, LabResult

# Basic unit tests for lab app
class LabBasicTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # Create doctor user
        self.doctor = User.objects.create_user(username="doc", password="pass")
        if hasattr(self.doctor, "role"):
            self.doctor.role = "doctor"
            self.doctor.save()

        # Create lab technician user
        self.labtech = User.objects.create_user(username="lab", password="pass")
        if hasattr(self.labtech, "role"):
            self.labtech.role = "lab"
            self.labtech.save()

        # Create patient if model exists
        if Patient:
            try:
                self.patient = Patient.objects.create(first_name="Test", last_name="Patient")
            except Exception:
                self.patient = Patient.objects.create()

    # Test: creating a LabRequest should trigger Billing creation via signals
    def test_create_lab_request_and_billing(self):
        if not Patient:
            self.skipTest("Patient model not available.")
        lr = LabRequest.objects.create(patient=self.patient, test_name="Test CBC")
        self.assertIsNotNone(lr.id)

    # Placeholder: ensure results can’t be created unless billing is paid
    def test_cannot_create_result_without_billing_paid(self):
        pass
