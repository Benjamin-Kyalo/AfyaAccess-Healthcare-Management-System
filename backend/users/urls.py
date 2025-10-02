from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# Register UserViewSet with DRF router (auto-generates CRUD API routes)
router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = router.urls
