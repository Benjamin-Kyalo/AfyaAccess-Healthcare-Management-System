from rest_framework import serializers
from .models import LabRequest, LabResult

# Try importing Billing model for payment checks
try:
    from billing.models import Billing
except Exception:
    Billing = None


# Serializer for LabRequest
class LabRequestSerializer(serializers.ModelSerializer):
    # Computed fields for frontend display
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

    # Display patient name
    def get_patient_display(self, obj):
        p = getattr(obj, "patient", None)
        if not p:
            return None
        first = getattr(p, "first_name", None)
        last = getattr(p, "last_name", None)
        if first or last:
            return f"{first or ''} {last or ''}".strip()
        return str(p)

    # Show price from LabRequest model
    def get_price(self, obj):
        return obj.get_price()

    # Show whether billing entry exists for this request
    def get_billing_created(self, obj):
        if Billing is None:
            return False
        service_name = f"Lab Test: {obj.get_display_name()} (request_id={obj.id})"
        return Billing.objects.filter(patient=obj.patient, service=service_name).exists()


# Serializer for LabResult
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

    # Custom validation: block result creation if billing unpaid
    def validate(self, attrs):
        lab_request = attrs.get("lab_request") or getattr(self.instance, "lab_request", None)
        if lab_request is None:
            raise serializers.ValidationError("lab_request is required.")

        if Billing is None:
            raise serializers.ValidationError("Billing integration not available.")

        expected_service = f"Lab Test: {lab_request.get_display_name()} (request_id={lab_request.id})"
        billing = Billing.objects.filter(patient=lab_request.patient, service=expected_service).first()
        if not billing:
            raise serializers.ValidationError("No billing record found for this lab request.")
        if not billing.is_paid:
            raise serializers.ValidationError("Payment required before adding results.")
        return attrs

    # Auto-set performed_by from request user
    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user") and validated_data.get("performed_by") is None:
            validated_data["performed_by"] = request.user
        return super().create(validated_data)
