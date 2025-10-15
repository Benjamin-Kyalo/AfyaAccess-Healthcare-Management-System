from rest_framework import serializers
from .models import Drug, Dispense, DispenseLine, AuditLog
from consultation.models import PrescriptionItem  # safe to import here


class DrugSerializer(serializers.ModelSerializer):
    """Serializer for Drug model (inventory)."""

    class Meta:
        model = Drug
        fields = [
            "id",
            "name",
            "strength_or_pack",
            "quantity",
            "unit_price",
            "availability_status",
        ]


class DispenseLineSerializer(serializers.ModelSerializer):
    """Serializer for each line in a Dispense."""

    prescription_item = serializers.PrimaryKeyRelatedField(
        queryset=PrescriptionItem.objects.all()
    )
    drug = serializers.PrimaryKeyRelatedField(queryset=Drug.objects.all())
    drug_name = serializers.CharField(source="drug.name", read_only=True)  # convenience field

    class Meta:
        model = DispenseLine
        fields = [
            "id",
            "prescription_item",
            "drug",
            "drug_name",
            "quantity_dispensed",
            "unit_price_at_dispense",
        ]
        # id, drug_name, and unit_price are auto-filled, not user editable
        read_only_fields = ["id", "drug_name", "unit_price_at_dispense"]

    def create(self, validated_data):
        """Auto-set unit price from the drug model before saving."""
        drug = validated_data["drug"]
        validated_data["unit_price_at_dispense"] = drug.unit_price
        return super().create(validated_data)


class DispenseSerializer(serializers.ModelSerializer):
    """Serializer for a full Dispense, including multiple lines."""

    lines = DispenseLineSerializer(many=True)  # nested lines

    class Meta:
        model = Dispense
        fields = ["id", "prescription", "performed_by", "timestamp", "lines"]
        read_only_fields = ["id", "timestamp"]

    def create(self, validated_data):
        """
        Create both the Dispense and its related lines.
        """
        lines_data = validated_data.pop("lines")
        dispense = Dispense.objects.create(**validated_data)
        for line_data in lines_data:
            line_data["dispense"] = dispense  # attach parent dispense
            DispenseLineSerializer().create(line_data)
        return dispense

    def to_representation(self, instance):
        """Customize output to include nested line data."""
        rep = super().to_representation(instance)
        rep["lines"] = DispenseLineSerializer(instance.lines.all(), many=True).data
        return rep


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog entries."""

    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = ["id", "user", "user_name", "action", "timestamp", "details"]
