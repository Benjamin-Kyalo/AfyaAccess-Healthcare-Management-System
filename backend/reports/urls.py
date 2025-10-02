from django.urls import path
from . import views

# App namespace for URL reversing
app_name = "reports"

# Define all endpoints for reporting
urlpatterns = [
    # Overall system summary (users, patients, billing, consultations, triage)
    path("summary/", views.ReportSummaryView.as_view(), name="report-summary"),
    # Patients-specific reporting
    path("patients/", views.PatientReportView.as_view(), name="patient-report"),
    # Billing-specific reporting
    path("billing/", views.BillingReportView.as_view(), name="billing-report"),
    # Consultations-specific reporting
    path("consultations/", views.ConsultationReportView.as_view(), name="consultation-report"),
    # Triage-specific reporting
    path("triage/", views.TriageReportView.as_view(), name="triage-report"),
]
