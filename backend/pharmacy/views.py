# pharmacy/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Drug, Dispense, AuditLog
from .serializers import DrugSerializer, DispenseSerializer, AuditLogSerializer


# ViewSet for Drugs
class DrugViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for drugs in the pharmacy.
    """
    queryset = Drug.objects.all().order_by("name")
    serializer_class = DrugSerializer
    permission_classes = [IsAuthenticated]


# ViewSet for Dispenses
class DispenseViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for dispensing drugs to patients.
    """
    queryset = Dispense.objects.all().order_by("-timestamp")
    serializer_class = DispenseSerializer
    permission_classes = [IsAuthenticated]


# ViewSet for Audit Logs
class AuditLogViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for pharmacy audit logs.
    """
    queryset = AuditLog.objects.all().order_by("-timestamp")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
