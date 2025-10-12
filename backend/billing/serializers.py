# billing/serializers.py
"""
Serializers for Billing and Payment models.
- BillingSerializer exposes nested payments (read-only) and computed balance.
- PaymentSerializer records created_by from request for audit.
"""

from decimal import Decimal
from rest_framework import serializers
from .models import Billing, Payment, SERVICE_DEFAULT_AMOUNTS


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment ledger entries."""

    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "billing", "amount", "payment_method", "reference_number", "created_by", "created_by_name", "created_at"]
        read_only_fields = ["created_at", "created_by_name"]

    def get_created_by_name(self, obj):
        """Human readable name for created_by (if available)."""
        if obj.created_by:
            return obj.created_by.get_full_name() or getattr(obj.created_by, "username", "")
        return None

    def create(self, validated_data):
        """Record created_by from request.user if not explicitly provided (audit)."""
        request = self.context.get("request")
        if request and hasattr(request, "user") and not validated_data.get("created_by"):
            validated_data["created_by"] = request.user
        return super().create(validated_data)


class BillingSerializer(serializers.ModelSerializer):
    """
    Billing serializer:
    - payments: nested list (read-only)
    - balance: computed from model helper
    - most server-generated fields are read-only to avoid accidental overrides
    """

    patient_bills = serializers.SerializerMethodField(read_only=True)  # your original helper
    payments = PaymentSerializer(many=True, read_only=True)
    balance = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Billing
        fields = [
            "id",
            "patient",
            "patient_name",
            "service",
            "amount",
            "currency",
            "invoice_number",
            "status",
            "charged_by",
            "charged_by_name",
            "charged_at",
            "created_at",
            "updated_at",
            "is_paid",
            "payments",
            "balance",
            "patient_bills",
            "lab_request",
            "dispense",
            "report_reference",
        ]
        read_only_fields = [
            "charged_at",
            "amount",
            "charged_by",
            "charged_by_name",
            "patient_name",
            "invoice_number",
            "created_at",
            "updated_at",
            "is_paid",
            "payments",
            "balance",
        ]

    def get_patient_bills(self, obj):
        """Return a quick list of this patient's bills (keeps your original idea)."""
        if obj.patient:
            bills_qs = obj.patient.billings.all().order_by("-created_at").values(
                "service", "amount", "is_paid", "charged_at", "invoice_number", "status"
            )
            return list(bills_qs)
        return []

    def get_balance(self, obj):
        """Return outstanding balance for this billing."""
        return obj.calculate_balance()

    def validate(self, attrs):
        """
        Ensure amounts (if provided) are non-negative.
        Prevent direct toggling of is_paid via serializer.
        """
        if self.instance and "is_paid" in attrs and attrs.get("is_paid") != self.instance.is_paid:
            raise serializers.ValidationError({"is_paid": "Change payment status via payment endpoints."})

        amt = attrs.get("amount")
        if amt is not None:
            try:
                amt_dec = Decimal(str(amt))
            except Exception:
                raise serializers.ValidationError({"amount": "Invalid amount format."})
            if amt_dec < Decimal("0.00"):
                raise serializers.ValidationError({"amount": "Amount must be >= 0."})
        return attrs

    def create(self, validated_data):
        """Set charged_by from request.user by default (preserves original behavior)."""
        request = self.context.get("request")
        if request and hasattr(request, "user") and not validated_data.get("charged_by"):
            validated_data["charged_by"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        If user attempts to set status to paid via API, prefer creating a payment
        for the outstanding balance to keep an audit trail. Otherwise, allow update.
        """
        incoming_status = validated_data.get("status")
        if incoming_status and incoming_status == Billing.STATUS_PAID:
            balance = instance.calculate_balance()
            request = self.context.get("request")
            user = request.user if request and hasattr(request, "user") else None
            if balance > Decimal("0.00"):
                instance.create_payment(amount=balance, method="manual", reference="admin-mark-paid", user=user)
            validated_data.pop("status", None)
        return super().update(instance, validated_data)
