from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BeToBeViewSet, MeetingViewSet

router = DefaultRouter()
router.register(r'btob', BeToBeViewSet)
router.register(r'meetings', MeetingViewSet)

urlpatterns = [
    path("organisateur/", include(router.urls)),
]
