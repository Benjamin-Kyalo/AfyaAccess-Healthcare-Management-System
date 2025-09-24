# backend/api/urls.py
# Routes for the `api` app.

from django.urls import path, include
from . import views

urlpatterns = [
    # GET /api/health/ -> health_check view
    path("health/", views.health_check, name="api-health"),
    path("patients/", include("patients.urls")),
]
