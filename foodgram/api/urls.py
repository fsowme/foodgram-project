from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookmarkViewSet, FoodsViewSet, SubscribeViewSet


# snippet_detail = BookmarkViewSet.as_view({"delete": "destroy"})


router = DefaultRouter()
router.register("food", FoodsViewSet, basename="food")
router.register("subscribe", SubscribeViewSet, basename="subscribe")
router.register("favorites", BookmarkViewSet, basename="favorites")


urlpatterns = [
    # path("v1/favorites/<slug:slug>/", snippet_detail, name="snippet-detail"),
    path("v1/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
