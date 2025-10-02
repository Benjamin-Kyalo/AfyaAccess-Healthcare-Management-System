# backend/patients/serializers.py
from rest_framework import serializers
from .models import Patient
from datetime import date

class PatientSerializer(serializers.ModelSerializer):
    # Read-only canonical id
    patient_number = serializers.CharField(read_only=True)
    # computed age
    age = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Patient
        fields = (
            "id",
            "patient_number",
            "first_name",
            "last_name",
            "dob",
            "gender",
            "national_id",
            "phone_number",
            "address",
            "created_by",
            "status",
            "created_at",
            "updated_at",
            "age"
        )
        read_only_fields = ("patient_number", "created_at", "updated_at", "created_by", "dob")
        extra_kwargs = {
            "first_name": {"help_text": "First name", "style": {"placeholder": "e.g. John"}},
            "last_name": {"help_text": "Last name", "style": {"placeholder": "e.g. Doe"}},
            "dob": {"help_text": "Date of birth YYYY-MM-DD", "style": {"placeholder": "YYYY-MM-DD"}},
            "national_id": {"help_text": "National ID (if available)", "style": {"placeholder": "e.g. 12345678"}},
            "phone_number": {"help_text": "Phone in international format", "style": {"placeholder": "+254712345678"}},
            "address": {"help_text": "Address (optional)", "style": {"placeholder": "Street, County"}},
        }

    # compute age dynamically
    def get_age(self, obj):
        if not obj.dob:
            return None
        today = date.today()
        born = obj.dob
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class PatientCreateSerializer(serializers.ModelSerializer):
    """
    Use this for create requests. The view calls the service; serializer only validates the data shape.
    """
    dob = serializers.DateField(
        required=False, 
        allow_null=True,
        input_formats=['%Y-%m-%d'],  # parses strings like 'YYYY-MM-DD' into date
    )

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "dob", "gender", "national_id", "phone_number", "address")