# pharmacy/serializers.py
from rest_framework import serializers
from .models import Drug, Dispense, DispenseLine, AuditLog
from consultation.models import PrescriptionItem  # safe to import here

class DrugSerializer(serializers.ModelSerializer):
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
    prescription_item = serializers.PrimaryKeyRelatedField(
        queryset=PrescriptionItem.objects.all()
    )
    drug = serializers.PrimaryKeyRelatedField(queryset=Drug.objects.all())
    drug_name = serializers.CharField(source="drug.name", read_only=True)

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
        read_only_fields = ["id", "drug_name", "unit_price_at_dispense"]

    def create(self, validated_data):
        """
        Auto-fill unit_price_at_dispense from the drug's current unit_price.
        """
        drug = validated_data["drug"]
        validated_data["unit_price_at_dispense"] = drug.unit_price
        return super().create(validated_data)


class DispenseSerializer(serializers.ModelSerializer):
    lines = DispenseLineSerializer(many=True)

    class Meta:
        model = Dispense
        fields = ["id", "prescription", "performed_by", "timestamp", "lines"]
        read_only_fields = ["id", "timestamp"]

    def create(self, validated_data):
        """
        Create Dispense and DispenseLine rows.
        DispenseLine.save() reduces stock (model logic).
        The outer view should call this inside a transaction + select_for_update() on Drug rows.
        """
        lines_data = validated_data.pop("lines")
        dispense = Dispense.objects.create(**validated_data)
        for line_data in lines_data:
            # attach dispense reference so DispenseLineSerializer.create() works
            line_data["dispense"] = dispense
            DispenseLineSerializer().create(line_data)
        return dispense

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["lines"] = DispenseLineSerializer(instance.lines.all(), many=True).data
        return rep


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = ["id", "user", "user_name", "action", "timestamp", "details"]
