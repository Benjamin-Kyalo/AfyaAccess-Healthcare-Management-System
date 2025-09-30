from django.test import TestCase
from django.contrib.auth import get_user_model
from patients.models import Patient
from .models import TriageRecord

User = get_user_model()

class TriageRecordTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="doctor1", password="testpass")
        self.patient = Patient.objects.create(
            full_name="John Doe",
            age=30,
            gender="Male"
        )

    def test_create_triage_record(self):
        record = TriageRecord.objects.create(
            patient=self.patient,
            attended_by=self.user,
            temperature_c=37.0,
            heart_rate_bpm=75,
            respiratory_rate_bpm=18,
            systolic_bp=120,
            diastolic_bp=80,
            spo2_percent=98.0,
            weight_kg=70,
            height_cm=175,
        )
        self.assertEqual(record.patient.full_name, "John Doe")
        self.assertEqual(record.attended_by.username, "doctor1")
        self.assertAlmostEqual(record.bmi, 22.86, places=2)
