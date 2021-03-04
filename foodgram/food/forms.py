from django import forms
from django.forms import fields, modelformset_factory
from django.forms.formsets import BaseFormSet
from django.forms.models import inlineformset_factory

from .models import Food, Ingredient, Recipe


class BaseIngredientFormSet(BaseFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["my_field"] = forms.CharField()


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


IngredientFormSet = inlineformset_factory(
    Recipe,
    Ingredient,
    form=IngredientForm,
    extra=0,
    formset=BaseIngredientFormSet,
)
