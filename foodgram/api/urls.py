from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FoodsViewSet, SubscribeViewSet

router = DefaultRouter()
router.register("food", FoodsViewSet, basename="food")
router.register("subscribe", SubscribeViewSet, basename="subscribe")

urlpatterns = [
    path("v1/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
