# Import the default Django User model
from django.contrib.auth.models import User
# Import serializer tools from Django REST Framework
from rest_framework import serializers

# Serializer for registering a new user
class RegisterSerializer(serializers.ModelSerializer):
    # Password should only be written (not exposed in API responses)
    password = serializers.CharField(write_only=True)

    class Meta:
        # This serializer will use the built-in User model
        model = User
        # Fields we allow to be handled in this serializer
        fields = ("id", "username", "email", "password")

    # Overriding create method to properly hash password
    def create(self, validated_data):
        # Create user with hashed password (instead of plain text)
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user
