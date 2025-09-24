from rest_framework import serializers
from .models import Billing

class BillingSerializer(serializers.ModelSerializer):
    patient_bills = serializers.SerializerMethodField()

    class Meta:
        model = Billing
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
            "patient_bills",   # show all patient bills
        ]
        read_only_fields = [
            "charged_at",
            "amount",
            "charged_by",
            "charged_by_name",
            "patient_name",
        ]

    def get_patient_bills(self, obj):
        if obj.patient:
            bills = obj.patient.billings.all().values(
                "service", "amount", "is_paid", "charged_at"
            )
            return list(bills)
        return []

    def validate(self, attrs):
        # Allow auto-created bills (is_paid=False) to pass
        # Only enforce validation if updating manually
        if self.instance and not attrs.get("is_paid", self.instance.is_paid):
            raise serializers.ValidationError(
                {"is_paid": "Payment must be confirmed before saving billing record."}
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["charged_by"] = user
        return super().create(validated_data)
