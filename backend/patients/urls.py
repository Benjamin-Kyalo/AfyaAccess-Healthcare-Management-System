from rest_framework.routers import DefaultRouter
from .views import PatientViewSet

# Use DRF router to automatically create routes
router = DefaultRouter()
router.register(r'patients', PatientViewSet)

urlpatterns = router.urls
