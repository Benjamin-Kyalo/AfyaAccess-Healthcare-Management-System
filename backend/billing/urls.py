# billing/urls.py
from rest_framework.routers import DefaultRouter
from .views import BillingViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r"billing", BillingViewSet, basename="billing")
router.register(r"payments", PaymentViewSet, basename="payments")

urlpatterns = router.urls
