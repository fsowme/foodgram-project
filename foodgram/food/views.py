import re

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from food.forms import IngredientForm, RecipeForm

from .models import Food, Ingredient, Recipe, Tag

FORMSET_COUNTER = ["form-TOTAL_FORMS", "form-INITIAL_FORMS"]


def make_pagination(request, elements, total_on_page):
    paginator = Paginator(elements, total_on_page)
    page_number = request.GET.get("page", 1)
    page = paginator.get_page(page_number)
    return paginator, page


def recipes_tags(recipes):
    tags_and_recipes = (
        Tag.objects.filter(recipes__in=recipes)
        .values("recipes", "name")
        .order_by("recipes")
    )
    tags_on_recipes = {}
    for tag_and_recipe in tags_and_recipes:
        recipe_id, tag_name = tag_and_recipe["recipes"], tag_and_recipe["name"]
        if not tags_on_recipes.get(recipe_id):
            tags_on_recipes[recipe_id] = [tag_name]
        else:
            tags_on_recipes[recipe_id].append(tag_name)
    return {"tags_on_recipes": tags_on_recipes}


def get_fullname_or_username(user):
    if user.first_name and user.last_name:
        return {"author_name": f"{user.first_name} {user.last_name}"}
    return {"author_name": f"{user.username}"}


def get_ingredients(recipe):
    ingredients_in_recipe = recipe.ingredients.values(
        "food__name", "amount", "food__unit", "food"
    )
    ingredients = []
    for i in ingredients_in_recipe:
        ingredients.append(
            {
                "food_name": i["food__name"],
                "amount": i["amount"],
                "food_unit": i["food__unit"],
                "food_id": i["food"],
            }
        )
    return {"ingredients": ingredients}


def update_post(data, field, prefix="form"):
    pattern = re.compile(rf"{prefix}-\d+-{field}")
    count = 0
    for key in data:
        if re.fullmatch(pattern, key):
            count += 1
    data = data.copy()
    data.update({_: count for _ in FORMSET_COUNTER})
    return data


def main(request):
    recipes = Recipe.objects.all()
    paginator, page = make_pagination(request, recipes, 6)
    context = {"page": page, "paginator": paginator}
    context.update(recipes_tags(page.object_list))
    return render(request, "index.html", context)


def recipe_view(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    tags_names = [tag["name"] for tag in recipe.tag.values("name")]
    context = {"recipe": recipe, "tags": tags_names}
    context.update(get_fullname_or_username(recipe.author))
    return render(request, "recipe_page.html", context)


@login_required
def recipe_edit(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    if request.user != recipe.author:
        return redirect("recipe", recipe_slug=recipe_slug)
    IngredientFormSet = modelformset_factory(
        Ingredient, form=IngredientForm, extra=0
    )
    ingredients = recipe.ingredients.all()
    if request.method == "POST":
        post_data = update_post(request.POST, field="name")
        formset = IngredientFormSet(post_data, request.FILES)
        for idx, form in enumerate(formset.forms):
            food_name, unit = form["name"].value(), form["unit"].value()
            if food := Food.objects.filter(name=food_name, unit=unit).first():
                if not Ingredient.objects.filter(food=food, recipe=recipe):
                    amount = form["amount"].value() or None
                    Ingredient.objects.create(
                        food=food, recipe=recipe, amount=amount
                    )

        return redirect("recipe", recipe_slug=recipe_slug)
    elif request.method == "GET":
        formset = IngredientFormSet(queryset=recipe.ingredients.all())
        for idx, ingredient in enumerate(recipe.ingredients.all()):
            formset.forms[idx]["name"].initial = ingredient.food.name
            formset.forms[idx]["unit"].initial = ingredient.food.unit
    tags_names = [tag["name"] for tag in recipe.tag.values("name")]
    recipe_form = RecipeForm(
        request.POST or None, request.FILES or None, instance=recipe
    )
    context = {
        "form": recipe_form,
        "tags": tags_names,
        "formset": formset,
    }
    context.update(get_ingredients(recipe))
    return render(request, "recipe_edit_page.html", context)


# def test(request):
#     IngredientFormSet = formset_factory(IngredientForm)
#     ingredient_formset = IngredientFormSet(request.POST or None)
#     for form in ingredient_formset.forms:
#         if form.is_valid():
#             instance = form.save(commit=False)
#             instance.recipe = Recipe.objects.get(pk=23)
#             instance.save()
#     return render(request, "qwe.html", {"formset": ingredient_formset})
