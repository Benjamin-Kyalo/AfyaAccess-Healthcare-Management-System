# afyaaccess/urls.py
from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter

# Users, Patients, Billing
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
# These are the CRUD endpoints for the consultation app.
router.register(r'consultations', ConsultationViewSet, basename="consultation")
router.register(r'prescriptions', PrescriptionViewSet, basename="prescription")
router.register(r'prescription-items', PrescriptionItemViewSet, basename="prescriptionitem")
router.register(r'investigations', InvestigationViewSet, basename="investigation")
router.register(r'diagnoses', DiagnosisViewSet, basename="diagnosis")

# -----------------------
# Pharmacy routes (grouped under /api/)
# -----------------------
# Using 'pharmacy/...' in route path keeps endpoints grouped and readable.
router.register(r'pharmacy/drugs', DrugViewSet, basename="pharmacy-drug")
router.register(r'pharmacy/dispenses', DispenseViewSet, basename="pharmacy-dispense")
router.register(r'pharmacy/auditlogs', AuditLogViewSet, basename="pharmacy-auditlog")

# Note:
# - If you later want to make consultation or pharmacy fully self-contained
#   you can add `path("api/consultation/", include("consultation.urls"))` and/or
#   `path("api/pharmacy/", include("pharmacy.urls"))` in addition to or instead
#   of these registrations — but avoid including both router registrations
#   and app `include()` for the *same* endpoints, as that leads to duplicate routes.
#
# Example (commented):
# path("api/consultation/", include("consultation.urls")),
# path("api/pharmacy/", include("pharmacy.urls")),

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
