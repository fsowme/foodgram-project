from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FoodsViewSet, SubscriptionsViewSet, test

router = DefaultRouter()
router.register("food", FoodsViewSet, basename="food")
# router.register("subscriptions", SubscriptionsViewSet, basename="subscribe")


urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/subscriptions/", test),
    path("api-auth/", include("rest_framework.urls")),
]
