from food.models import Follow, Food
from rest_framework import serializers


class FoodSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="name")
    dimension = serializers.CharField(source="unit")

    class Meta:
        model = Food
        fields = ["title", "dimension"]


class SubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ["user", "author"]
