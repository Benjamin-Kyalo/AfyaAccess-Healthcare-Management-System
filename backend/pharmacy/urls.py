# pharmacy/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DrugViewSet, DispenseViewSet, AuditLogViewSet

router = DefaultRouter()
router.register(r"drugs", DrugViewSet, basename="drug")
router.register(r"dispenses", DispenseViewSet, basename="dispense")
router.register(r"auditlogs", AuditLogViewSet, basename="auditlog")

urlpatterns = router.urls
