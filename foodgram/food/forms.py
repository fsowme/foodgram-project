from django import forms
from django.forms import BaseInlineFormSet, widgets
from django.forms.models import InlineForeignKeyField, inlineformset_factory
from django.http import request

from .models import Food, Ingredient, Recipe, Tag


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
    tag = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=widgets.CheckboxSelectMultiple(
            attrs={"class": "tags__checkbox"}
        ),
        required=False,
    )
    ings = forms.ModelMultipleChoiceField(queryset=None)

    class Meta:
        model = Recipe
        fields = [
            "name",
            "tag",
            "image",
            "description",
            "cooking_time",
            "food",
            "amount",
        ]

    # def clean(self):
    # super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ings"].queryset = Ingredient.objects.filter(
            recipe=self.instance
        )

    # def clean_ings(self):
    #     print("CLEANED_DATA:______________")
    #     print(self.cleaned_data)
    #     print("DATA:______________")
    #     print(self.data)
    #     print("fields[ings]:______________")
    #     print(self.fields["ings"])
    #     self.instance.ingredients.set(self.cleaned_data["ings"])
    # return


# def __init__(self, *args, **kwargs):
#     super().__init__(*args, **kwargs)
#     self.fields['ings'].queryset =


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
