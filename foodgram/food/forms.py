from django import forms
from django.forms import fields, modelformset_factory

from .models import Food, Ingredient, Recipe


class IngredientForm(forms.ModelForm):
    name = forms.CharField()
    unit = forms.CharField()

    class Meta:
        model = Ingredient
        fields = ["amount"]


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["name", "image", "description", "cooking_time"]


IngredientFormSet = modelformset_factory(
    Ingredient, form=IngredientForm, extra=0
)
