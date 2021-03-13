from django import forms
from django.forms import widgets
from django.shortcuts import get_object_or_404

from food.models import Food, Ingredient, Recipe, Tag


class RecipeForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=widgets.CheckboxSelectMultiple(),
    )
    amount = forms.MultipleChoiceField(required=False)
    food = forms.MultipleChoiceField(required=False)

    class Meta:
        model = Recipe
        fields = [
            "name",
            "description",
            "cooking_time",
            "tags",
            "image",
        ]
        labels = {
            "name": ("Название рецепта"),
            "description": ("Описание рецепта"),
            "cooking_time": ("Время приготовления"),
            "tags": ("Тэги"),
            "image": ("Вкуная картинка"),
            "food": ("Ингредиенты"),
            "amount": ("Количество ингредиента"),
        }
        help_text = {
            "name": ("Придуймайте название рецепта"),
            "description": ("Подробно опишите процесс приголовления"),
            "cooking_time": ("Сколько времени всё это займет в минутах"),
            "tags": ("К какой категории отностися этот рецепт"),
            "image": ("Загрузите какое-нибудь фото"),
            "food": ("Укажите нежные продукты"),
            "amount": ("Количество продуктов"),
        }

    def clean_food(self):
        food_names = self.data.getlist("nameIngredient")
        food_units = self.data.getlist("unitsIngredient")
        food_amount = self.data.getlist("valueIngredient")
        if len(food_names) != len(food_units) != len(food_amount):
            raise forms.ValidationError(
                "Number of titles does not equal number of units and "
                "amount of products"
            )
        food = zip(food_names, food_units)
        cleaned_food = {}
        for count, (name, unit) in enumerate(food):
            ingredient = get_object_or_404(Food, name=name, unit=unit)
            cleaned_food[ingredient] = food_amount[count]
        self.cleaned_data["food"] = cleaned_food
        return self.cleaned_data["food"]

    def save(self, commit=True):
        super().save(commit=False)
        self.instance.author = self.initial["author"]
        self.instance.save()
        self.instance.tags.set(self.cleaned_data["tags"])
        ingredients = self.cleaned_data["food"]
        Ingredient.objects.filter(recipe=self.instance).exclude(
            food__in=ingredients.keys()
        ).delete()
        for food, amount in ingredients.items():
            Ingredient.objects.update_or_create(
                recipe=self.instance, food=food, defaults={"amount": amount}
            )
        return self.instance
