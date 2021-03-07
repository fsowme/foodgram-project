from django import forms
from django.forms import widgets

from .models import Food, Ingredient, Recipe, Tag


class RecipeForm(forms.ModelForm):
    tag = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=widgets.CheckboxSelectMultiple(),
        required=False,
    )
    # image = forms.ImageField(required=False)
    amount = forms.MultipleChoiceField(required=False)
    food = forms.MultipleChoiceField(required=False)

    class Meta:
        model = Recipe
        fields = [
            "name",
            "description",
            "cooking_time",
            "tag",
            "image",
        ]
        # widgets = {
        #     "tags": forms.CheckboxSelectMultiple(),
        # }

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
        keys = []
        for count, (name, unit) in enumerate(food):
            if (
                Food.objects.filter(name=name, unit=unit).exists()
                and Food.objects.get(name=name, unit=unit).pk not in keys
            ):
                ingredient = Food.objects.get(name=name, unit=unit)
                cleaned_food[ingredient] = food_amount[count]
        self.cleaned_data["food"] = cleaned_food
        print(cleaned_food, self.cleaned_data["food"], "*******")
        return self.cleaned_data["food"]

    def clean_image(self):
        print(self.cleaned_data)
        return self.cleaned_data["image"]
