from django.http.response import Http404, HttpResponse
from django.shortcuts import render
from food.models import Food
from rest_framework import mixins, viewsets

from .serializers import FoodSerializer


class FoodsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FoodSerializer

    def get_queryset(self):
        if query := self.request.query_params.get("query"):
            foods = Food.objects.filter(name__istartswith=query)
            return foods
        raise Http404("No query parameter.")
