from django import forms
from django.forms import BaseInlineFormSet, widgets
from django.forms.models import InlineForeignKeyField

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
    food = forms.MultipleChoiceField(required=False)
    amount = forms.MultipleChoiceField(required=False)

    class Meta:
        model = Recipe
        fields = [
            "name",
            "tag",
            "image",
            "description",
            "cooking_time",
        ]

    def clean(self):
        super().clean()
        food_names = self.data.getlist("nameIngredient")
        food_units = self.data.getlist("unitsIngredient")
        food_amount = self.data.getlist("valueIngredient")
        if len(food_names) != len(food_units) != len(food_amount):
            raise forms.ValidationError(
                "Number of titles does not equal number of units and "
                "amount of products"
            )
        # cleaned_amount = []
        # for idx, food in enumerate(food_names):
        #     unit, amount = unit[idx], food_amount[idx]
        #     if Food.objects.filter(name=food, unit=unit).exists():
        print(food_names, food_amount, food_units)
        food = zip(food_names, food_units)
        keys = []
        cleaned_amount = []
        for count, (name, unit) in enumerate(food):
            if (
                Food.objects.filter(name=name, unit=unit).exists()
                and Food.objects.get(name=name, unit=unit).pk not in keys
            ):
                cleaned_amount.append(food_amount[count])
                keys.append(Food.objects.get(name=name, unit=unit).pk)
        print(keys)
        self.cleaned_data["food"] = Food.objects.filter(pk__in=keys)
        self.cleaned_data["amount"] = cleaned_amount
        self.instance.ingredients.all().delete()

        print(self.cleaned_data["food"])
        print(self.cleaned_data["amount"])
        for idx, item in enumerate(self.cleaned_data["food"]):
            Ingredient.objects.create(
                recipe=self.instance,
                food=item,
                amount=self.cleaned_data["amount"][idx],
            )
        # print(self.cleaned_data["amount"])
        # return Food.objects.filter(pk__in=set(keys))

    # def clean_food(self):
    #     super().clean()
    #     print(self.cleaned_data["food"])

    #     food_names = self.data.getlist("nameIngredient")
    #     food_units = self.data.getlist("unitsIngredient")
    #     amount = self.data.getlist("valueIngredient")
    #     if len(food_names) != len(food_units) != len(amount):
    #         raise forms.ValidationError(
    #             "Number of titles does not equal number of units and "
    #             "amount of products"
    #         )
    #     food = zip(food_names, food_units)
    #     keys = []
    #     for count, (name, unit) in enumerate(food):
    #         if not Food.objects.filter(name=name, unit=unit).exists():
    #             del amount[count]
    #         else:
    #             keys.append(Food.objects.get(name=name, unit=unit).pk)
    #     self.data["amount"] = amount
    #     return Food.objects.filter(pk__in=set(keys))

    # def clean_amount(self):
    #     print("INGS " * 10)
    #     print(self.data)
    #     super().clean()
    #     # self.fields["ingredients"].queryset
    #     amount = self.data.getlist("valueIngredient")

    # def clean(self):
    #     super().clean()

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if self.instance.pk:
    #         self.fields[
    #             "ingredients"
    #         ].queryset = self.instance.ingredients.all()
    #     else:
    #         self.fields["ingredients"].queryset = Ingredient.objects.none()

    # def clean(self):
    # super().clean()

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
