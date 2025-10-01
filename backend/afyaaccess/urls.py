# afyaaccess/urls.py
from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter

# Users, Patients, Billing
from lab.views import LabRequestViewSet, LabResultViewSet
from users.views import UserViewSet
from patients.views import PatientViewSet
from billing.views import BillingViewSet

# Consultation viewsets (already implemented in consultation.views)
from consultation.views import (
    ConsultationViewSet,
    PrescriptionViewSet,
    PrescriptionItemViewSet,
    InvestigationViewSet,
    DiagnosisViewSet,
)

# Pharmacy viewsets
from pharmacy.views import (
    DrugViewSet,
    AuditLogViewSet,
    DispenseViewSet,
)

# Router
router = DefaultRouter()

# -----------------------
# Core modules
# -----------------------
router.register(r'users', UserViewSet, basename="user")
router.register(r'patients', PatientViewSet, basename="patient")
router.register(r'billing', BillingViewSet, basename="billing")

# -----------------------
# Consultation routes
# -----------------------
router.register(r'consultations', ConsultationViewSet, basename="consultation")
router.register(r'prescriptions', PrescriptionViewSet, basename="prescription")
router.register(r'prescription-items', PrescriptionItemViewSet, basename="prescriptionitem")
router.register(r'investigations', InvestigationViewSet, basename="investigation")
router.register(r'diagnoses', DiagnosisViewSet, basename="diagnosis")

# -----------------------
# Pharmacy routes
# -----------------------
router.register(r'pharmacy/drugs', DrugViewSet, basename="pharmacy-drug")
router.register(r'pharmacy/dispenses', DispenseViewSet, basename="pharmacy-dispense")
router.register(r'pharmacy/auditlogs', AuditLogViewSet, basename="pharmacy-auditlog")

# -----------------------
# Lab routes
# -------------------
router.register(r'labs/requests', LabRequestViewSet, basename="lab-request")
router.register(r'labs/results', LabResultViewSet, basename="lab-result")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),

    # -----------------------
    # Triage app endpoints
    # -----------------------
    path("api/triage/", include("triage.urls", namespace="triage")),

    # -----------------------
    # Reports app endpoints
    # -----------------------
    path("api/reports/", include("reports.urls")),   # ✅ Added reports
]
