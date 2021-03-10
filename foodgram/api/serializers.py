from food.models import Bookmark, Follow, Food, Purchase, Recipe
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from users.models import User


class FoodSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="name")
    dimension = serializers.CharField(source="unit")

    class Meta:
        model = Food
        fields = ["title", "dimension"]


class SubscriptionsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field="username"
    )
    user = serializers.SlugRelatedField(
        default=CurrentUserDefault(), read_only=True, slug_field="pk"
    )

    class Meta:
        model = Follow
        lookup_field = "author__username"
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


class PurchaseSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        default=CurrentUserDefault(), read_only=True, slug_field="pk"
    )
    recipe = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(), slug_field="slug"
    )

    class Meta:
        model = Purchase
        lookup_field = "recipe__slug"
        fields = ["user", "recipe"]


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = "__all__"
