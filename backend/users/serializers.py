from rest_framework import serializers
from .models import User

# Serializer to control how User data is exposed in the API
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Only expose selected safe fields (not password, etc.)
        fields = ["id", "username", "email", "designation"]
