from django.db import models
from django.http.response import Http404, HttpResponse
from django.shortcuts import render
from food.models import Bookmark, Follow, Food
from rest_framework import mixins, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .custom_viewsets import CreateDestroyViewSet
from .serializers import (
    BookmarkSerializer,
    FoodSerializer,
    SubscriptionsSerializer,
)


class FoodsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FoodSerializer

    def get_queryset(self):
        if query := self.request.query_params.get("query"):
            foods = Food.objects.filter(name__istartswith=query)
            return foods
        raise Http404("No query parameter.")


class SubscribeViewSet(viewsets.ModelViewSet):
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


class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    queryset = Bookmark.objects.all()
    lookup_field = "recipe__slug"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"success": True})

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"success": True})
