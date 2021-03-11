from django.contrib import admin

from food.models import (
    Bookmark,
    Follow,
    Food,
    Ingredient,
    Purchase,
    Recipe,
    Tag,
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author_username", "pub_date")
    search_fields = ("name",)

    def author_username(self, obj):
        return obj.author.username


class FoodAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "counted")
    search_fields = ("name",)


admin.site.register(Bookmark)
admin.site.register(Follow)
admin.site.register(Food, FoodAdmin)
admin.site.register(Ingredient)
admin.site.register(Purchase)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
