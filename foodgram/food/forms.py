from django import forms
from django.forms import (
    BaseInlineFormSet,
    fields,
    modelformset_factory,
    widgets,
)
from django.forms.models import InlineForeignKeyField, inlineformset_factory

from .models import Food, Ingredient, Recipe


class IngredientForm(forms.ModelForm):
    food_name = forms.MultipleChoiceField()
    food_unit = forms.CharField()

    class Meta:
        model = Ingredient
        fields = ["amount", "food"]

    def clean_food(self):
        name = self["food_name"]
        unit = self["food_unit"]
        if food := Food.objects.filter(name=name, unit=unit).first():
            self.instance.food = food.pk
        else:
            self.instance.food = None


class IngredientBaseFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super(IngredientBaseFormSet, self).add_fields(form, index)
        instance = self.get_queryset()[index]
        form.fields["food_name"] = forms.CharField(
            initial=instance.food.name, required=False
        )
        form.fields["food_unit"] = forms.CharField(
            initial=instance.food.unit, required=False
        )
        form.fields["food"] = InlineForeignKeyField(
            parent_instance=instance.food
        )

    def clean(self):
        super().clean()
        for form in self.forms:
            name = form.cleaned_data["food_name"]
            unit = form.cleaned_data["food_unit"]
            if food := Food.objects.filter(name=name, unit=unit).first():
                form.instance.food = food
            # else:
            #     form.instance.food = None


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ["food", "recipe", "amount"]

    def clean(self):
        pass


class RecipeForm(forms.ModelForm):
    food_name = forms.MultipleChoiceField(
        required=False,
        widget=widgets.SelectMultiple(attrs={"is_hidden": True}),
    )
    food_unit = forms.MultipleChoiceField(
        required=False,
        widget=widgets.SelectMultiple(attrs={"is_hidden": True}),
    )
    ingredients = forms.ModelChoiceField(queryset=Ingredient.objects.all())

    class Meta:
        model = Recipe
        fields = [
            "name",
            "tag",
            "image",
            "description",
            "cooking_time",
            "ingredient",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ingredients"].queryset = Ingredient.objects.filter(
            recipe=self.instance
        )


# class IngredientForm(forms.ModelForm):
#     food_name = forms.MultipleChoiceField()
#     food_unit = forms.CharField()

#     class Meta:
#         model = Ingredient
#         fields = ["amount", "food"]

#     def clean_food(self):
#         name = self["food_name"]
#         unit = self["food_unit"]
#         if food := Food.objects.filter(name=name, unit=unit).first():
#             self.instance.food = food.pk
#         else:
#             self.instance.food = None
