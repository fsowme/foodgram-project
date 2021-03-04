from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FoodsViewSet

router = DefaultRouter()
router.register("food", FoodsViewSet, basename="food")

urlpatterns = [
    path("v1/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
