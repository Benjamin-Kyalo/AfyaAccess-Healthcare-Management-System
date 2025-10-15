# Import Django path for routing
from django.urls import path
# Import JWT login and refresh token views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# Import custom registration view
from .views import RegisterView

# Define URL endpoints for authentication
urlpatterns = [
    # Register a new user
    path("register/", RegisterView.as_view(), name="register"),
    # Login and get JWT tokens (access + refresh)
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Refresh token endpoint (get new access token using refresh token)
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
