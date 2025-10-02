from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Patient
from .serializers import PatientSerializer

# Patient API endpoints
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]  # only logged-in users allowed

    def perform_create(self, serializer):
        # Automatically set 'created_by' to the logged-in user
        serializer.save(created_by=self.request.user)
