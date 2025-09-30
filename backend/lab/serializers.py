# lab/serializers.py
"""
DRF serializers for LabRequest and LabResult.
LabResultSerializer enforces the payment check: results can be created only if the associated
billing row is marked paid.
"""
from rest_framework import serializers
from .models import LabRequest, LabResult

# Try importing Billing; if absent, validation will raise an informative error
try:
    from billing.models import Billing
except Exception:
    Billing = None


class LabRequestSerializer(serializers.ModelSerializer):
    patient_display = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    billing_created = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LabRequest
        fields = [
            "id",
            "patient",
            "patient_display",
            "consultation",
            "investigation",
            "test_name",
            "price",
            "status",
            "notes",
            "requested_at",
            "billing_created",
        ]
        read_only_fields = ("requested_at", "price", "billing_created", "patient_display")

    def get_patient_display(self, obj):
        p = getattr(obj, "patient", None)
        if not p:
            return None
        # try common name fields otherwise fallback to str()
        first = getattr(p, "first_name", None)
        last = getattr(p, "last_name", None)
        if first or last:
            return f"{first or ''} {last or ''}".strip()
        return str(p)

    def get_price(self, obj):
        # price is computed from investigation if available
        return obj.get_price()

    def get_billing_created(self, obj):
        """
        Return boolean whether a billing entry exists for this LabRequest.
        We look up by patient + service convention. This is a convenience field for the frontend.
        """
        if Billing is None:
            return False
        service_name = f"Lab Test: {obj.get_display_name()} (request_id={obj.id})"
        return Billing.objects.filter(patient=obj.patient, service=service_name).exists()


class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = [
            "id",
            "lab_request",
            "performed_by",
            "result_text",
            "result_json",
            "file_upload",
            "created_at",
            "verified",
        ]
        read_only_fields = ("created_at",)

    def validate(self, attrs):
        # Ensure Billing model is available and that the lab_request has a paid billing row
        lab_request = attrs.get("lab_request") or getattr(self.instance, "lab_request", None)
        if lab_request is None:
            raise serializers.ValidationError("lab_request is required.")

        if Billing is None:
            raise serializers.ValidationError("Billing integration not available on the server. Check billing app import.")

        # We match billing service using a convention created in signals.py:
        expected_service = f"Lab Test: {lab_request.get_display_name()} (request_id={lab_request.id})"
        billing = Billing.objects.filter(patient=lab_request.patient, service=expected_service).first()
        if not billing:
            raise serializers.ValidationError("No billing record found for this lab request. Contact billing.")
        if not billing.is_paid:
            # Important: do not allow creation of results if not paid
            raise serializers.ValidationError("Payment required before adding results.")
        return attrs

    def create(self, validated_data):
        # auto-populate performed_by from request user if possible
        request = self.context.get("request")
        if request and hasattr(request, "user") and validated_data.get("performed_by") is None:
            validated_data["performed_by"] = request.user
        return super().create(validated_data)
