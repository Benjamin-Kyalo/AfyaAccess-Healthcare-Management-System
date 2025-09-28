# consultation/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ConsultationViewSet,
    PrescriptionViewSet,
    PrescriptionItemViewSet,
    InvestigationViewSet,
    DiagnosisViewSet,
)

router = DefaultRouter()
router.register(r'consultations', ConsultationViewSet, basename="consultation")
router.register(r'prescriptions', PrescriptionViewSet, basename="prescription")
router.register(r'prescription-items', PrescriptionItemViewSet, basename="prescriptionitem")
router.register(r'investigations', InvestigationViewSet, basename="investigation")
router.register(r'diagnoses', DiagnosisViewSet, basename="diagnosis")

urlpatterns = [
    path("", include(router.urls)),
]
