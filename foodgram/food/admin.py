from django.contrib import admin

from food.models import Follow, Food, Ingredient, Recipe, Tag

admin.site.register(Follow)
admin.site.register(Food)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Tag)
