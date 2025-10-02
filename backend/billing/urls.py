from rest_framework.routers import DefaultRouter
from .views import BillingViewSet

# Router automatically generates RESTful endpoints
router = DefaultRouter()
router.register(r'billing', BillingViewSet)

# Expose router URLs
urlpatterns = router.urls
