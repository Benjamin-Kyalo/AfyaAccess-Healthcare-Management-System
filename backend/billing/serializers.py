from rest_framework import serializers
from .models import Billing

# Serializer for Billing model
class BillingSerializer(serializers.ModelSerializer):
    # Custom field to list all bills of the patient
    patient_bills = serializers.SerializerMethodField()

    class Meta:
        model = Billing
        # Fields exposed in API
        fields = [
            "id",
            "patient",
            "patient_name",
            "service",
            "amount",
            "charged_by",
            "charged_by_name",
            "charged_at",
            "is_paid",
            "patient_bills",   # include related patient bills
        ]
        # Fields that cannot be changed directly
        read_only_fields = [
            "charged_at",
            "amount",
            "charged_by",
            "charged_by_name",
            "patient_name",
        ]

    # Return all bills for the same patient
    def get_patient_bills(self, obj):
        if obj.patient:
            bills = obj.patient.billings.all().values(
                "service", "amount", "is_paid", "charged_at"
            )
            return list(bills)
        return []

    # Validation for marking payments
    def validate(self, attrs):
        # Allow auto-created bills (default unpaid)
        # Prevent changing unpaid -> paid without confirmation
        if self.instance and not attrs.get("is_paid", self.instance.is_paid):
            raise serializers.ValidationError(
                {"is_paid": "Payment must be confirmed before saving billing record."}
            )
        return attrs

    # Automatically assign the user who created the bill
    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["charged_by"] = user
        return super().create(validated_data)
