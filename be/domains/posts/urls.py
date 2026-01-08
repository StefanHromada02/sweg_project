from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

router = DefaultRouter()
router.register(r"", PostViewSet)  # /api/posts/

urlpatterns = [
    path("", include(router.urls)),
]