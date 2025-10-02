from rest_framework import serializers
from .models import Patient, PatientStatusHistory

# Serializer for patient status history records
class PatientStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientStatusHistory
        fields = ("id", "old_status", "new_status", "changed_by", "note", "timestamp")


# Serializer for patient model
class PatientSerializer(serializers.ModelSerializer):
    # Include patient’s status history (nested, read-only)
    status_history = PatientStatusHistorySerializer(many=True, read_only=True)

    # Redefine gender choices for API validation
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("intersex", "Intersex"),
        ("other", "Other"),
    ]
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=False, allow_blank=True)

    class Meta:
        model = Patient
        fields = (
            "id", "first_name", "last_name", "age", "gender",
            "national_id", "phone", "status", "registered_at",
            "created_by", "status_history",
        )
        # System-controlled fields are read-only
        read_only_fields = ("status", "registered_at", "created_by", "status_history")

    def validate(self, data):
        # Prevent creation of duplicate patient records
        if Patient.objects.filter(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            national_id=data.get("national_id"),
            phone=data.get("phone")
        ).exists():
            raise serializers.ValidationError(
                "A patient with identical details already exists."
            )
        return data
