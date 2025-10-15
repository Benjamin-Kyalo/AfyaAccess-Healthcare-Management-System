# Import generic views (e.g., CreateAPIView)
from rest_framework import generics
# Import Django's built-in User model
from django.contrib.auth.models import User
# Import our custom serializer
from .serializers import RegisterSerializer

# View for registering new users
class RegisterView(generics.CreateAPIView):
    # Queryset defines all users in the database
    queryset = User.objects.all()
    # Use our custom serializer for handling registration
    serializer_class = RegisterSerializer
