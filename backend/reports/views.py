# reports/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Import models from other apps
# from backend import triage
from users.models import User
from patients.models import Patient
from billing.models import Billing
from consultation.models import Consultation
from triage.models import TriageRecord


class ReportSummaryView(APIView):
    """
    Returns a high-level summary of key system metrics.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {
            "total_users": User.objects.count(),
            "total_patients": Patient.objects.count(),
            "total_bills": Billing.objects.count(),
            "paid_bills": Billing.objects.filter(is_paid=True).count(),
            "unpaid_bills": Billing.objects.filter(is_paid=False).count(),
            "total_consultations": Consultation.objects.count(),
            "total_triages": triage.objects.count(),
        }
        return Response(data)


class PatientReportView(APIView):
    """
    Returns summary data related to patients.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {
            "total_patients": Patient.objects.count(),
            "male_patients": Patient.objects.filter(gender="Male").count(),
            "female_patients": Patient.objects.filter(gender="Female").count(),
        }
        return Response(data)


class BillingReportView(APIView):
    """
    Returns summary data related to billing.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {
            "total_bills": Billing.objects.count(),
            "paid_bills": Billing.objects.filter(is_paid=True).count(),
            "unpaid_bills": Billing.objects.filter(is_paid=False).count(),
        }
        return Response(data)


class ConsultationReportView(APIView):
    """
    Returns summary data related to consultations.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {
            "total_consultations": Consultation.objects.count(),
        }
        return Response(data)


class TriageReportView(APIView):
    """
    Returns summary data related to triage records.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {
            "total_triages": Triage.objects.count(),
        }
        return Response(data)
