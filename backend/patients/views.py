from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Patient
from .serializers import PatientSerializer, PatientCreateSerializer
from .permissions import IsReceptionOrAdmin
from .services import register_patient, find_possible_matches

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by("-created_at")
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsReceptionOrAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return PatientCreateSerializer
        return PatientSerializer

    def perform_create(self, serializer):
        # We don't want to call serializer.save() directly because we want to use the service
        # But DRF calls perform_create after validated_data; for our flow, override create() instead.
        return super().perform_create(serializer)

    def create(self, request, *args, **kwargs):
        data = request.data
        result = register_patient(data, created_by=request.user)
        if not result["created"]:
            # return 409 Conflict with list of possible matches (serialized)
            matches = result["matches"]
            serialized = PatientSerializer(matches, many=True, context={"request": request})
            return Response(
                {"detail": "Possible existing patients found.", "matches": serialized.data},
                status=status.HTTP_409_CONFLICT,
            )
        # created True
        patient = result["patient"]
        serialized = PatientSerializer(patient, context={"request": request})
        return Response(serialized.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="matches")
    def matches(self, request):
        """
        GET /api/patients/matches/?q=... will search for duplicates using phone/national_id/name+dob extracted from q.
        For more structured checks, use the register endpoint which returns matches when present.
        """
        q = request.query_params.get("q", "").strip()
        if not q:
            return Response({"detail": "provide q param (phone/national_id/name)"}, status=status.HTTP_400_BAD_REQUEST)

        # Try to interpret q: phone or national id or name
        # Very simple heuristics; your frontend can call more structured endpoint.
        data = {"phone_number": q, "national_id": q}
        matches = find_possible_matches(data)
        serialized = PatientSerializer(matches, many=True, context={"request": request})
        return Response(serialized.data)
