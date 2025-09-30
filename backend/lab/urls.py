# lab/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabRequestViewSet, LabResultViewSet

router = DefaultRouter()
router.register(r"requests", LabRequestViewSet, basename="lab-request")
router.register(r"results", LabResultViewSet, basename="lab-result")

urlpatterns = [
    path("", include(router.urls)),
]
