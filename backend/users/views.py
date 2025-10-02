from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer

# ViewSet gives full CRUD API (list, create, update, delete) for User model
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # All users in system
    serializer_class = UserSerializer  # Use serializer for API representation
