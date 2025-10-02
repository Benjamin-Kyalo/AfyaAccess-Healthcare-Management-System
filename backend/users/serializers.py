"""
- UserSerializer: for safe public representation (no password).
- RegistrationSerializer: for creating users (password write-only).
"""
from click import style
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # read-only list of group names for display
    groups = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "designation",
            "phone_number",
            "department",
            "groups",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
        # extra_kwargs = {
        #     "username": {"help_text": "Choose a unique username", "style": {"placeholder": "Enter username"}},
        #     "email": {"help_text": "Enter a valid email", "style": {"placeholder": "e.g. john@example.com"}},
        #     "first_name": {"help_text": "Enter first name", "style": {"placeholder": "e.g. John"}},
        #     "last_name": {"help_text": "Enter last name", "style": {"placeholder": "e.g. Doe"}},
        #     "phone_number": {"style": {"placeholder": "+254712345678"}},
        # }

    def get_groups(self, obj):
        return [g.name for g in obj.groups.all()]


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Use to register a user (admin-only or open registration depending on your route).
    - Enforces unique email and min password length.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password", "placeholder": "Enter a strong password"},
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "designation",
            "phone_number",
            "department",
        )
        
        extra_kwargs = {
            "username": {"help_text": "Unique username", "style": {"placeholder": "e.g. johndoe"}},
            "email": {"help_text": "Valid email required", "style": {"placeholder": "e.g. johndoe@example.com"}},
            "first_name": {"help_text": "First name", "style": {"placeholder": "e.g. John"}},
            "last_name": {"help_text": "Last name", "style": {"placeholder": "e.g. Doe"}},
            "phone_number": {"help_text": "Optional phone number", "style": {"placeholder": "+254712345678"}},
        }

    def validate_email(self, value):
        # Case-insensitive uniqueness guard
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def create(self, validated_data):
        # Use create_user to ensure password hashing + any custom user creation logic.
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user
