from food.models import Food
from rest_framework import serializers


class FoodSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="name")
    dimension = serializers.CharField(source="unit")

    class Meta:
        model = Food
        fields = ["title", "dimension"]
