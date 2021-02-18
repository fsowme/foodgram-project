from django.contrib import admin

from .models import Food, Ingredient, Recipe, Tag

admin.site.register(Food)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Tag)
