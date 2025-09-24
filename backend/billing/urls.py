from rest_framework.routers import DefaultRouter
from .views import BillingViewSet

router = DefaultRouter()
router.register(r'billing', BillingViewSet)

urlpatterns = router.urls
