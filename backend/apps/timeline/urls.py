"""
Timeline URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TimelineEventViewSet

router = DefaultRouter()
router.register(r"", TimelineEventViewSet, basename="timeline")

urlpatterns = [
    path("", include(router.urls)),
]
