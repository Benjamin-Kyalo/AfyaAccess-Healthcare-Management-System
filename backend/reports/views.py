# reports/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Import models from other apps to gather report data
from users.models import User
from patients.models import Patient
from billing.models import Billing
from consultation.models import Consultation
from triage.models import TriageRecord 


# Returns a high-level summary of key hospital system metrics
class ReportSummaryView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def get(self, request, *args, **kwargs):
        # Collect key metrics across the system
        data = {
            "total_users": User.objects.count(),
            "total_patients": Patient.objects.count(),
            "total_bills": Billing.objects.count(),
            "paid_bills": Billing.objects.filter(is_paid=True).count(),
            "unpaid_bills": Billing.objects.filter(is_paid=False).count(),
            "total_consultations": Consultation.objects.count(),
            "total_triages": TriageRecord.objects.count(),  # fixed typo
        }
        return Response(data)


# Returns statistics about patients
class PatientReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {
            "total_patients": Patient.objects.count(),
            "male_patients": Patient.objects.filter(gender="Male").count(),
            "female_patients": Patient.objects.filter(gender="Female").count(),
        }
        return Response(data)


# Returns billing summary (paid vs unpaid bills)
class BillingReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {
            "total_bills": Billing.objects.count(),
            "paid_bills": Billing.objects.filter(is_paid=True).count(),
            "unpaid_bills": Billing.objects.filter(is_paid=False).count(),
        }
        return Response(data)


# Returns statistics about consultations
class ConsultationReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {
            "total_consultations": Consultation.objects.count(),
        }
        return Response(data)


# Returns statistics about triage records
class TriageReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {
            "total_triages": TriageRecord.objects.count(),  # fixed typo
        }
        return Response(data)
