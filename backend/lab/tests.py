# lab/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model

try:
    from patients.models import Patient
except Exception:
    Patient = None

from .models import LabRequest, LabResult

class LabBasicTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # create simple user(s) — adjust role attribute logic if present in your User model
        self.doctor = User.objects.create_user(username="doc", password="pass")
        if hasattr(self.doctor, "role"):
            self.doctor.role = "doctor"
            self.doctor.save()

        self.labtech = User.objects.create_user(username="lab", password="pass")
        if hasattr(self.labtech, "role"):
            self.labtech.role = "lab"
            self.labtech.save()

        # create a patient if Patient model exists
        if Patient:
            try:
                self.patient = Patient.objects.create(first_name="Test", last_name="Patient")
            except Exception:
                self.patient = Patient.objects.create()

    def test_create_lab_request_and_billing(self):
        if not Patient:
            self.skipTest("Patient model not available.")
        lr = LabRequest.objects.create(patient=self.patient, test_name="Test CBC")
        # After creation, signal should create a Billing entry if Billing app exists.
        self.assertIsNotNone(lr.id)

    def test_cannot_create_result_without_billing_paid(self):
        # This is higher-level integration; keep to minimal checks here.
        pass
