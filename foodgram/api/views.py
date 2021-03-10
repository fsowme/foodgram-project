from django.db import models
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from food.models import Bookmark, Follow, Food, Purchase
from rest_framework import mixins, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .custom_viewsets import CreateDestroyViewSet
from .serializers import (
    BookmarkSerializer,
    FoodSerializer,
    PurchaseSerializer,
    SubscriptionsSerializer,
)


class FoodsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FoodSerializer

    def get_queryset(self):
        if query := self.request.query_params.get("query"):
            foods = Food.objects.filter(name__istartswith=query)
            return foods
        raise Http404("No query parameter.")


class SubscribeViewSet(CreateDestroyViewSet):
    serializer_class = SubscriptionsSerializer
    queryset = Follow.objects.all()
    lookup_field = "author__username"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"success": True})

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"success": True})


class BookmarkViewSet(CreateDestroyViewSet):
    serializer_class = BookmarkSerializer
    lookup_field = "recipe__slug"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.request.user.bookmarks.all()
        return queryset

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"success": True})

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"success": True})


class PurchaseViewSet(CreateDestroyViewSet):
    serializer_class = PurchaseSerializer
    lookup_field = "recipe__slug"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        self.request.user.bookmarks.all()
        queryset = self.request.user.purchases.all()
        return queryset

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"success": True})

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"success": True})
