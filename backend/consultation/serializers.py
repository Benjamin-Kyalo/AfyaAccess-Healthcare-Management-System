from rest_framework import serializers
from .models import Consultation, Prescription, PrescriptionItem, Investigation, Diagnosis
from pharmacy.serializers import DrugSerializer
from pharmacy.models import Drug, AuditLog
from billing.models import Billing
from patients.models import Patient   


class VitalsSerializer(serializers.Serializer):
    # A plain serializer, no model — flexible JSON input/output for vitals
    sys = serializers.IntegerField(required=False)
    dia = serializers.IntegerField(required=False)
    pulse = serializers.IntegerField(required=False)
    temp = serializers.FloatField(required=False)
    rr = serializers.IntegerField(required=False)
    rbs = serializers.FloatField(required=False)
    spo2 = serializers.IntegerField(required=False)


class InvestigationSerializer(serializers.ModelSerializer):
    # Simple mapping for lab investigations (id, name, price, availability)
    class Meta:
        model = Investigation
        fields = ["id", "name", "price", "availability_status"]


class DiagnosisSerializer(serializers.ModelSerializer):
    # Straightforward serializer for diagnoses
    class Meta:
        model = Diagnosis
        fields = ["id", "name"]


class PrescriptionItemSerializer(serializers.ModelSerializer):
    # doctor selects drug by id; also expose full drug detail for UI
    drug = serializers.PrimaryKeyRelatedField(queryset=Drug.objects.all())
    drug_detail = DrugSerializer(source="drug", read_only=True)

    # Add human-readable dropdown labels (DRF convention)
    route_display = serializers.CharField(source="get_route_display", read_only=True)
    unit_display = serializers.CharField(source="get_unit_display", read_only=True)
    frequency_display = serializers.CharField(source="get_frequency_display", read_only=True)

    class Meta:
        model = PrescriptionItem
        fields = [
            "id",
            "drug",
            "drug_detail",
            "route",
            "route_display",
            "dose",
            "unit",
            "unit_display",
            "frequency",
            "frequency_display",
            "duration",
            "quantity_requested",
            "quantity_dispensed",
        ]
        read_only_fields = ["quantity_dispensed"]

    # Validation logic for numeric fields
    def validate_dose(self, value):
        if value is None:
            return value
        if value <= 0:
            raise serializers.ValidationError("dose must be a positive integer")
        return value

    def validate_duration(self, value):
        if value is None:
            return value
        if value <= 0:
            raise serializers.ValidationError("duration must be a positive integer (days)")
        return value

    def validate(self, attrs):
        # Optional: could enforce dose & duration always required for billing
        return attrs


class PrescriptionSerializer(serializers.ModelSerializer):
    # Nested serializer for multiple items inside a prescription
    items = PrescriptionItemSerializer(many=True)

    class Meta:
        model = Prescription
        fields = ["id", "consultation", "status", "created_by", "created_at", "items"]
        read_only_fields = ["status", "created_at"]

    def create(self, validated_data):
        # Override create to handle nested prescription items
        items = validated_data.pop("items", [])
        prescription = Prescription.objects.create(**validated_data)

        for item in items:
            PrescriptionItem.objects.create(prescription=prescription, **item)

        return prescription


class ConsultationSerializer(serializers.ModelSerializer):
    # Patient must have paid consultation bill before consultation is allowed
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.filter(
            billings__service="consultation",
            billings__is_paid=True
        ).distinct(),
        required=True
    )
    vitals = VitalsSerializer(required=False)

    investigations = serializers.PrimaryKeyRelatedField(
        queryset=Investigation.objects.all(),
        many=True,
        required=False
    )
    diagnoses = serializers.PrimaryKeyRelatedField(
        queryset=Diagnosis.objects.all(),
        many=True,
        required=False
    )
    prescriptions = PrescriptionSerializer(many=True, write_only=True, required=False)

    # Enriched read-only details for UI consumption
    investigations_detail = InvestigationSerializer(source="investigations", many=True, read_only=True)
    diagnoses_detail = DiagnosisSerializer(source="diagnoses", many=True, read_only=True)
    prescriptions_detail = PrescriptionSerializer(source="prescriptions", many=True, read_only=True)

    # Snapshot fields (doctor + patient names)
    patient_name = serializers.CharField(read_only=True)
    doctor_name = serializers.CharField(read_only=True)

    class Meta:
        model = Consultation
        fields = [
            "id",
            "patient",
            "patient_name",
            "doctor_name",
            "complaints",
            "history",
            "vitals",
            "investigations", "investigations_detail",
            "diagnoses", "diagnoses_detail",
            "created_by",
            "created_at",
            "prescriptions", "prescriptions_detail",
        ]
        read_only_fields = ["created_at", "patient_name", "doctor_name"]

    def create(self, validated_data):
        """
        Override to handle nested objects:
        - vitals stored as JSON
        - nested prescriptions created
        - automatic audit logging
        - billing for investigations
        """
        vitals_data = validated_data.pop("vitals", {})
        prescriptions_data = validated_data.pop("prescriptions", [])
        investigations = validated_data.pop("investigations", [])
        diagnoses = validated_data.pop("diagnoses", [])

        # Attach doctor automatically if not provided
        doctor = validated_data.get("created_by")
        if not doctor and self.context.get("request") and self.context["request"].user.is_authenticated:
            validated_data["created_by"] = self.context["request"].user
            doctor = self.context["request"].user

        patient = validated_data.get("patient")

        # Create consultation record
        consultation = Consultation.objects.create(
            **validated_data,
            vitals=vitals_data,
            patient_name=f"{patient.first_name} {patient.last_name}" if patient else "",
            doctor_name=doctor.get_full_name() if doctor else ""
        )

        # Set many-to-manys
        if investigations:
            consultation.investigations.set(investigations)
        if diagnoses:
            consultation.diagnoses.set(diagnoses)

        # Create prescriptions and items
        for presc in prescriptions_data:
            items = presc.pop("items", [])
            prescription = Prescription.objects.create(
                consultation=consultation,
                created_by=consultation.created_by
            )
            for it in items:
                PrescriptionItem.objects.create(prescription=prescription, **it)

            # Audit log for prescription creation
            AuditLog.objects.create(
                user=consultation.created_by,
                action=AuditLog.ACTION_PRESCRIPTION_CREATED,
                details={
                    "consultation_id": consultation.id,
                    "prescription_id": prescription.id,
                    "items": [
                        {
                            "drug": it["drug"].id if isinstance(it["drug"], Drug) else it["drug"],
                            "quantity_requested": it["quantity_requested"],
                            "route": it.get("route"),
                            "dose": it.get("dose"),
                            "unit": it.get("unit"),
                            "frequency": it.get("frequency"),
                            "duration": it.get("duration"),
                        }
                        for it in items
                    ],
                },
            )

        # Create billing entry for investigations
        Billing.objects.create(
            patient=consultation.patient,
            amount=sum(inv.price for inv in consultation.investigations.all()),
            is_paid=False,
        )

        return consultation
