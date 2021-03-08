from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from users.models import User

from .forms import RecipeForm
from .models import Follow, Ingredient, Recipe, Tag

FORMSET_COUNTER = ["{prefix}-TOTAL_FORMS", "{prefix}-INITIAL_FORMS"]


def make_pagination(request, elements, total_on_page):
    paginator = Paginator(elements, total_on_page)
    page_number = request.GET.get("page", 1)
    page = paginator.get_page(page_number)
    return paginator, page


def get_recipes_tags(recipes):
    return {
        "recipes_tags": {recipe.id: recipe.tag.all() for recipe in recipes}
    }


def get_authors_names(recipes):
    authors = {}
    for recipe in recipes:
        authors[recipe.id] = get_name(recipe.author)["author_name"]
    return {"authors_names": authors}


def get_authors(recipes):
    return {"authors": {recipe.id: recipe.author for recipe in recipes}}


def get_name(user):
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


def main(request):
    recipes = Recipe.objects.all()
    paginator, page = make_pagination(request, recipes, 6)
    context = {"page": page, "paginator": paginator, "tags": Tag.objects.all()}
    context.update(get_recipes_tags(page))
    context.update(get_authors(page))
    context.update(get_authors_names(page))
    return render(request, "index.html", context)


def is_editable(author, user):
    editable = bool(user.is_authenticated and user == author)
    return {"can_edit": editable}


def is_following(author, user):
    follow = bool(
        user.is_authenticated
        and Follow.objects.filter(author=author, user=user).exists()
    )
    return {"follow": follow}


def recipe_view(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    tags_names = recipe.tag.values("name", "eng_name", "color")
    context = {"recipe": recipe, "tags": tags_names}
    context.update(get_name(recipe.author))
    context.update(is_editable(recipe.author, request.user))
    return render(request, "recipe_page.html", context)


def user_view(request, username):
    author = get_object_or_404(User, username=username)
    recipes = author.recipes.all()
    paginator, page = make_pagination(request, recipes, 6)
    context = {"page": page, "paginator": paginator, "tags": Tag.objects.all()}
    context.update({"author": author})
    context.update(get_recipes_tags(page))
    context.update(get_name(author))
    context.update({"can_subscribe": author == request.user})
    return render(request, "index.html", context)


@login_required
def recipe_edit(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    if request.user != recipe.author:
        return redirect("recipe", recipe_slug=recipe_slug)
    recipe_form = RecipeForm(
        request.POST or None, files=request.FILES or None, instance=recipe
    )

    if recipe_form.is_valid():
        instance = recipe_form.save(commit=False)
        instance.author = request.user
        instance.tag.set(recipe_form.cleaned_data["tag"])
        ingredients = recipe_form.cleaned_data["food"]
        Ingredient.objects.exclude(food__in=ingredients.keys()).delete()
        for food, amount in ingredients.items():
            Ingredient.objects.update_or_create(
                recipe=recipe, food=food, defaults={"amount": amount}
            )
        instance.save()
        return redirect("recipe", recipe_slug=recipe_slug)
    context = {"form": recipe_form, "tags": Tag.objects.all()}
    context.update(get_ingredients(recipe))
    return render(request, "recipe_edit_page.html", context)


@login_required
def recipe_new(request):
    recipe_form = RecipeForm(request.POST or None, files=request.FILES or None)
    if recipe_form.is_valid():
        instance = recipe_form.save(commit=False)
        print(instance.author)
        instance.author = request.user
        instance.save()
        instance.tag.set(recipe_form.cleaned_data["tag"])
        ingredients = recipe_form.cleaned_data["food"]
        for food, amount in ingredients.items():
            Ingredient.objects.create(
                recipe=instance, food=food, amount=amount
            )
        return redirect("index")
    context = {"form": recipe_form, "tags": Tag.objects.all()}
    return render(request, "recipe_edit_page.html", context)


@login_required
def recipe_delete(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    if request.user != recipe.author:
        return redirect("recipe", recipe_slug=recipe_slug)
    recipe.delete()
    return redirect("index")
