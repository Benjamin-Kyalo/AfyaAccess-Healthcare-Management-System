from django.urls import path
from .views import (
    TriageRecordCreateView,
    PatientTriageListView,
    TodayTriageListView,
    VitalRangesView,
    PatientsListView,
)

app_name = "triage"

urlpatterns = [
    path("", TriageRecordCreateView.as_view(), name="triage-create"),
    path("patient/<int:patient_id>/", PatientTriageListView.as_view(), name="triage-patient-list"),
    path("today/", TodayTriageListView.as_view(), name="triage-today-list"),
    path("ranges/", VitalRangesView.as_view(), name="triage-ranges"),
    path("patients/", PatientsListView.as_view(), name="triage-patients-list"),
]
