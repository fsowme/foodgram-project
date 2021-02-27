from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

urlpatterns = [
    path("v1/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
