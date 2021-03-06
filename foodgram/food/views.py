import re

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from food.forms import RecipeForm

from .models import Ingredient, Recipe, Tag

FORMSET_COUNTER = ["{prefix}-TOTAL_FORMS", "{prefix}-INITIAL_FORMS"]


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
    data["ingredients-TOTAL_FORMS"] = str(count)
    # data["ingredients-INITIAL_FORMS"] = str(count)
    removed_idx = []
    for idx, key in enumerate(data):
        if data.get(f"ingredients-{idx}-recipe") and not data.get(
            f"ingredients-{idx}-food_name"
        ):
            removed_idx.append(idx)
    count = 0
    for idx in removed_idx:
        # del data[f"ingredients-{idx}-recipe"]
        # del data[f"ingredients-{idx}-id"]
        # del data[f"ingredients-{idx}-food"]
        data[f"ingredients-{idx}-DELETE"] = ""
    data["ingredients-TOTAL_FORMS"] = "1"
    data["ingredients-INITIAL_FORMS"] = "1"
    # data.update({_.format(prefix=prefix): count for _ in FORMSET_COUNTER})
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
    recipe_form = RecipeForm(
        request.POST or None,
        request.FILES or None,
        instance=recipe,
    )
    if recipe_form.is_valid():
        instance = recipe_form.save(commit=False)
        instance.author = request.user
        instance.save()
        # ingredient = zip(
        #     recipe_form.cleaned_data["food"],
        #     recipe_form.cleaned_data["amount"],
        # )
        # for food, amount in ingredient:
        #     Ingredient.objects.get_or_create(
        #         food=food, amount=amount, defaults={"recipe": recipe}
        #     )
        return redirect("recipe", recipe_slug=recipe_slug)
    context = {"form": recipe_form, "tags": Tag.objects.all()}
    context.update(get_ingredients(recipe))
    return render(request, "recipe_edit_page.html", context)


def recipe_delete(request):
    HttpResponse("OK")


@login_required
def recipe_new(request):
    recipe_form = RecipeForm(request.POST or None, request.FILES or None)
    if recipe_form.is_valid():
        recipe_form.save()
        return redirect("index")
    context = {"form": recipe_form, "tags": Tag.objects.all()}
    return render(request, "recipe_edit_page.html", context)
