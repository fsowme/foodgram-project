from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BookmarkViewSet,
    FoodsViewSet,
    PurchaseViewSet,
    SubscribeViewSet,
)

router = DefaultRouter()
router.register("food", FoodsViewSet, basename="food")
router.register("subscribe", SubscribeViewSet, basename="subscribe")
router.register("favorites", BookmarkViewSet, basename="favorite")
router.register("purchases", PurchaseViewSet, basename="purchase")


urlpatterns = [
    path("v1/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
