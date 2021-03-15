from api.custom_viewsets import CreateDestroyViewSet
from api.serializers import (
    BookmarkSerializer,
    FoodSerializer,
    PurchaseSerializer,
    SubscriptionsSerializer,
)
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from food.models import Follow, Food, Purchase, Recipe
from rest_framework import mixins, viewsets
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.response import Response


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


class BookmarkViewSet(CreateDestroyViewSet):
    serializer_class = BookmarkSerializer
    lookup_field = "recipe__slug"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.request.user.bookmarks.all()
        return queryset


class PurchaseViewSet(CreateDestroyViewSet):
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    serializer_class = PurchaseSerializer
    lookup_field = "recipe__slug"

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            recipe_slug = self.request.data.get("recipe")
            self.request.session[recipe_slug] = True

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Purchase.objects.none()
        return self.request.user.purchases.all()

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            slug = self.kwargs.get("recipe__slug")
            get_object_or_404(Recipe, slug=slug)
            if self.request.session.get(slug):
                del self.request.session[slug]
                return Response({"success": True})
            return Response({"success": False})
        return super().destroy(request, *args, **kwargs)
