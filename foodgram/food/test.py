from django.forms import modelformset_factory

from .forms import IngredientForm
from .models import Ingredient, Recipe

recipe = Recipe.objects.first()
IngredientFormSet = modelformset_factory(Ingredient, form=IngredientForm)
formset = IngredientFormSet(quertset=recipe.ingredients.all())
print(formset)
