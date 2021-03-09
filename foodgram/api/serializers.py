from rest_framework.fields import CurrentUserDefault
from food.models import Bookmark, Follow, Food, Recipe
from rest_framework import serializers

from users.models import User


class FoodSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="name")
    dimension = serializers.CharField(source="unit")

    class Meta:
        model = Food
        fields = ["title", "dimension"]


class SubscriptionsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field="pk"
    )
    user = serializers.SlugRelatedField(
        default=CurrentUserDefault(), read_only=True, slug_field="pk"
    )

    class Meta:
        model = Follow
        lookup_field = "author"
        fields = ["user", "author"]


class BookmarkSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        default=CurrentUserDefault(), read_only=True, slug_field="pk"
    )
    recipe = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(), slug_field="slug"
    )

    class Meta:
        model = Bookmark
        lookup_field = "recipe__slug"
        fields = ["user", "recipe"]

    def get_value(self, dictionary):
        print(dictionary)
        return super().get_value(dictionary)