from rest_framework import generics, status
from rest_framework import serializers
from rest_framework.response import Response
from django.utils.timezone import now
from .models import TriageRecord
from .serializers import TriageRecordSerializer
from patients.models import Patient
from .utils import analyze_vitals, VITAL_RANGES

# ---------------------------
# CREATE NEW TRIAGE RECORD
# ---------------------------
class TriageRecordCreateView(generics.CreateAPIView):
    queryset = TriageRecord.objects.all()
    serializer_class = TriageRecordSerializer

    def perform_create(self, serializer):
        # Attach logged-in user as attending clinician
        serializer.save(attended_by=self.request.user)

    def create(self, request, *args, **kwargs):
        # Override default response to add vitals summary
        response = super().create(request, *args, **kwargs)
        record = TriageRecord.objects.get(id=response.data["id"])
        analysis = analyze_vitals(record)
        response.data["summary"] = analysis
        return response


# ---------------------------
# LIST TRIAGE FOR SPECIFIC PATIENT
# ---------------------------
class PatientTriageListView(generics.ListAPIView):
    serializer_class = TriageRecordSerializer

    def get_queryset(self):
        patient_id = self.kwargs["patient_id"]
        return TriageRecord.objects.filter(patient_id=patient_id).order_by("-created_at")


# ---------------------------
# LIST TODAY'S TRIAGE RECORDS
# ---------------------------
class TodayTriageListView(generics.ListAPIView):
    serializer_class = TriageRecordSerializer

    def get_queryset(self):
        today = now().date()
        return TriageRecord.objects.filter(created_at__date=today).order_by("-created_at")


# ---------------------------
# LIST ALL VITAL RANGES (reference for frontend placeholders/alerts)
# ---------------------------
from rest_framework.views import APIView

class VitalRangesView(APIView):
    def get(self, request):
        return Response(VITAL_RANGES)


# ---------------------------
# LIST ALL PATIENTS (for dropdown in triage entry UI)
# ---------------------------
class PatientsListView(generics.ListAPIView):
    """
    Provides a simple patient list for frontend dropdown.
    """
    queryset = Patient.objects.all().order_by("first_name")
    serializer_class = serializers.Serializer  # Placeholder, we override list method

    def list(self, request, *args, **kwargs):
        # Return only IDs + names for dropdowns
        patients = Patient.objects.all().values("id", "full_name")
        return Response(list(patients))
