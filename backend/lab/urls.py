from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabRequestViewSet, LabResultViewSet

# Router auto-generates CRUD endpoints
router = DefaultRouter()
router.register(r"requests", LabRequestViewSet, basename="lab-request")
router.register(r"results", LabResultViewSet, basename="lab-result")

# Include router-generated URLs
urlpatterns = [
    path("", include(router.urls)),
]
