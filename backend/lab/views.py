"""
DRF ViewSets for LabRequest and LabResult for easy router registration.
- LabRequestViewSet: doctors can create requests; others can list/view.
- LabResultViewSet: lab techs can create results (serializer enforces billing paid); anyone authenticated can list/view.
"""
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import LabRequest, LabResult
from .serializers import LabRequestSerializer, LabResultSerializer
from .permissions import IsDoctor, IsLabTechOrReadOnly
from rest_framework.permissions import IsAuthenticated

# ViewSet for LabRequest
class LabRequestViewSet(viewsets.ModelViewSet):
    queryset = LabRequest.objects.all().select_related("patient", "investigation")
    serializer_class = LabRequestSerializer
    permission_classes = [IsAuthenticated]  # creation guarded more strictly via action-level permissions

    def get_permissions(self):
        # POST (create) allowed only for doctors
        if self.action in ("create",):
            return [IsAuthenticated(), IsDoctor()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Ensure the test_name default if investigation is provided
        inv = serializer.validated_data.get("investigation")
        if inv and not serializer.validated_data.get("test_name"):
            serializer.validated_data["test_name"] = getattr(inv, "name", "")
        serializer.save()

# ViewSet for LabResult
class LabResultViewSet(viewsets.ModelViewSet):
    queryset = LabResult.objects.all().select_related("lab_request", "performed_by")
    serializer_class = LabResultSerializer
    permission_classes = [IsAuthenticated, IsLabTechOrReadOnly]

    def create(self, request, *args, **kwargs):
        """
        Create will be blocked at serializer.validate if billing isn't paid.
        """
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsDoctor])
    def verify(self, request, pk=None):
        """
        Mark a LabResult as verified by a senior user/doctor.
        """
        try:
            result = self.get_object()
            result.verified = True
            result.save()
            return Response({"status": "verified"})
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
