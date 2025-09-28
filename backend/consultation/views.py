# consultation/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Consultation, Prescription, PrescriptionItem, Investigation, Diagnosis
from .serializers import (
    ConsultationSerializer,
    PrescriptionSerializer,
    PrescriptionItemSerializer,
    InvestigationSerializer,
    DiagnosisSerializer,
)

# ViewSet for Consultations
class ConsultationViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD for Consultation records.
    Automatically manages nested prescriptions, investigations, and diagnoses.
    """
    queryset = Consultation.objects.all().order_by("-created_at")
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]


# ViewSet for Prescriptions
class PrescriptionViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD for Prescriptions (linked to Consultations).
    """
    queryset = Prescription.objects.all().order_by("-created_at")
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]


# ViewSet for Prescription Items
class PrescriptionItemViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD for individual Prescription Items.
    """
    queryset = PrescriptionItem.objects.all()
    serializer_class = PrescriptionItemSerializer
    permission_classes = [IsAuthenticated]


# ViewSet for Investigations
class InvestigationViewSet(viewsets.ModelViewSet):
    """
    CRUD for Investigations (like lab tests).
    """
    queryset = Investigation.objects.all()
    serializer_class = InvestigationSerializer
    permission_classes = [IsAuthenticated]


# ViewSet for Diagnoses
class DiagnosisViewSet(viewsets.ModelViewSet):
    """
    CRUD for Diagnoses.
    """
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer
    permission_classes = [IsAuthenticated]
