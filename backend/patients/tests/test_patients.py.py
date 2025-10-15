# backend/patients/tests/test_patients.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Patient
from datetime import date, timedelta

User = get_user_model()

class PatientsAPITestCase(APITestCase):
    def setUp(self):
        # create reception user and admin
        self.admin = User.objects.create_superuser(username="admin", email="a@a.com", password="adminpass123")
        self.reception = User.objects.create_user(username="recept", email="r@r.com", password="receptpass")
        # add reception to Reception group if group exists (optional)
        from django.contrib.auth.models import Group
        grp, _ = Group.objects.get_or_create(name="Reception")
        self.reception.groups.add(grp)

        self.list_url = reverse("patient-list")

    def test_reception_can_create_patient(self):
        self.client.force_authenticate(user=self.reception)
        payload = {
            "first_name": "Alice",
            "last_name": "Buyer",
            "dob": str(date.today() - timedelta(days=365*30)),
            "national_id": "12345",
            "phone_number": "+254700000001",
            "address": "Nairobi"
        }
        resp = self.client.post(self.list_url, payload, format="json")
        # either created or conflict if duplicates logic triggers (should be created)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("patient_number", resp.data)
        # verify patient number format PAT-
        self.assertTrue(resp.data["patient_number"].startswith("PAT-"))

    def test_duplicate_detection_returns_409(self):
        # create an existing patient
        p = Patient.objects.create(first_name="Bob", phone_number="+254700000002")
        self.client.force_authenticate(user=self.reception)
        payload = {
            "first_name": "Bob",
            "phone_number": "+254700000002",
        }
        resp = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("matches", resp.data)
        self.assertTrue(len(resp.data["matches"]) >= 1)

    def test_age_computation(self):
        dob = date.today().replace(year=date.today().year - 25)
        p = Patient.objects.create(first_name="Sam", dob=dob)
        self.client.force_authenticate(user=self.admin)
        url = reverse("patient-detail", args=[p.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["age"], 25)
