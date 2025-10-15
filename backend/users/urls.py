"""
Users app URLs.
- Provides extra routes like /api/users/register/
- Uses DRF DefaultRouter for consistency
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from .serializers import RegistrationSerializer
from rest_framework import generics


# Optional open registration view (if you want to allow sign-up)
class RegisterView(generics.CreateAPIView):
    """
    Public registration endpoint.
    Uses RegistrationSerializer to validate and create a new user.
    You can restrict this with IsAdminUser if you want admin-only creation.
    """
    serializer_class = RegistrationSerializer


# Router just for user viewset
router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    # /api/users/register/ → registration endpoint
    path("register/", RegisterView.as_view(), name="user-register"),
]

# Include router.urls so /api/users/ still works
urlpatterns += router.urls
