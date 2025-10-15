"""
Users API endpoints using a ModelViewSet.
- Enforces IsAdminOrSelf for object-level safety.
- Adds basic search + ordering.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .serializers import UserSerializer, RegistrationSerializer
from .permissions import IsAdminOrSelf

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "phone_number", "groups__name"]
    ordering_fields = ["created_at", "username"]

    # If you want a separate registration endpoint (open), create a custom view using RegistrationSerializer.
