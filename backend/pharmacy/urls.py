from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DrugViewSet, DispenseViewSet, AuditLogViewSet

# Router auto-generates CRUD routes for viewsets
router = DefaultRouter()
router.register(r"drugs", DrugViewSet, basename="drug")
router.register(r"dispenses", DispenseViewSet, basename="dispense")
router.register(r"auditlogs", AuditLogViewSet, basename="auditlog")

# Final list of URLs
urlpatterns = router.urls
