from rest_framework import serializers
from .models import TriageRecord
from patients.models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()

class TriageRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for Triage Records.
    Includes patient name + ID and attending user name + ID for readability.
    """
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)

    attended_by_name = serializers.CharField(source="attended_by.username", read_only=True)
    attended_by_id = serializers.IntegerField(source="attended_by.id", read_only=True)


    class Meta:
        model = TriageRecord
        fields = [
            "id",
            "patient", "patient_id", "patient_name",
            "attended_by", "attended_by_id", "attended_by_name",
            "temperature_c", "heart_rate_bpm", "respiratory_rate_bpm",
            "systolic_bp", "diastolic_bp", "spo2_percent",
            "weight_kg", "height_cm", "bmi",
            "created_at"
        ]
        read_only_fields = [
            "bmi", "created_at",
            "patient_name", "patient_id",
            "attended_by_name", "attended_by_id"
        ]

    def validate(self, data):
        """Check that temperature values are realistic."""
        if data.get("temperature_c") and (20 > data["temperature_c"] or data["temperature_c"] > 45):
            raise serializers.ValidationError("Temperature must be between 20°C and 45°C.")
        return data
