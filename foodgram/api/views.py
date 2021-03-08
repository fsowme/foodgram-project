from django.http.response import Http404, HttpResponse
from django.shortcuts import render
from food.models import Follow, Food
from rest_framework import mixins, viewsets

from .serializers import FoodSerializer, SubscriptionsSerializer


class FoodsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FoodSerializer

    def get_queryset(self):
        if query := self.request.query_params.get("query"):
            foods = Food.objects.filter(name__istartswith=query)
            return foods
        raise Http404("No query parameter.")


class SubscriptionsViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionsSerializer

    def create(self, request, *args, **kwargs):
        print(request.POST)
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        print("***************************")
        print(self.request)
        return Follow.objects.all()


def test(request):
    print(request.POST, "************")
    return HttpResponse("OK")
