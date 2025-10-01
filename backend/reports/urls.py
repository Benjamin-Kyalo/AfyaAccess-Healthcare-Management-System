# reports/urls.py
from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("summary/", views.ReportSummaryView.as_view(), name="report-summary"),
    path("patients/", views.PatientReportView.as_view(), name="patient-report"),
    path("billing/", views.BillingReportView.as_view(), name="billing-report"),
    path("consultations/", views.ConsultationReportView.as_view(), name="consultation-report"),
    path("triage/", views.TriageReportView.as_view(), name="triage-report"),
]
