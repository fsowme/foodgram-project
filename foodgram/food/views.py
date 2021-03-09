from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from pytils.translit import slugify
from users.models import User

from .forms import RecipeForm
from .models import Bookmark, Follow, Ingredient, Recipe, Tag

INDEX_PAGE_SIZE = 6
FOLLOW_PAGE_SIZE = 3
BOOKMARK_PAGE_SIZE = 6
RECIPES_FOLLOW_PAGE = 3


def make_pagination(request, elements, total_on_page):
    paginator = Paginator(elements, total_on_page)
    page_number = request.GET.get("page")
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


def is_editable(author, user):
    editable = bool(user.is_authenticated and user == author)
    return {"can_edit": editable}


def is_subscribed(author, user):
    subscribed = bool(Follow.objects.filter(author=author, user=user).exists())
    return {"subscribed": subscribed}


def can_subscribe(author, user):
    return {"can_subscribe": bool(user.is_authenticated and user != author)}


def check_bookmark(user, recipe):
    in_bookmark = bool(
        user.is_authenticated
        and Bookmark.objects.filter(user=user, recipe=recipe).exists()
    )
    return {"in_bookmark": in_bookmark}


def recipes_in_bookmarks(user, recipes):
    bookmarks = {_.id: check_bookmark(user, _)["in_bookmark"] for _ in recipes}
    return {"bookmarks": bookmarks}


@login_required
def bookmarks_view(request):
    user = request.user
    recipes = Recipe.objects.filter(in_bookmark__user=user)
    paginator, page = make_pagination(request, recipes, BOOKMARK_PAGE_SIZE)
    context = {"paginator": paginator, "page": page, "tags": Tag.objects.all()}
    context.update(get_recipes_tags(page))
    context.update(get_authors(page))
    context.update(get_authors_names(page))
    context.update(recipes_in_bookmarks(user, recipes))
    return render(request, "index.html", context)


def main(request):
    recipes = Recipe.objects.all()
    paginator, page = make_pagination(request, recipes, INDEX_PAGE_SIZE)
    context = {"page": page, "paginator": paginator, "tags": Tag.objects.all()}
    context.update(get_recipes_tags(page))
    context.update(get_authors(page))
    context.update(get_authors_names(page))
    if request.user.is_authenticated:
        context.update(recipes_in_bookmarks(request.user, recipes))
    return render(request, "index.html", context)


def recipe_view(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    tags_names = recipe.tag.values("name", "eng_name", "color")
    context = {"recipe": recipe, "tags": tags_names, "author": recipe.author}
    context.update(get_name(recipe.author))
    context.update(is_editable(recipe.author, request.user))
    context.update(can_subscribe(recipe.author, request.user))
    if request.user.is_authenticated:
        context.update(is_subscribed(recipe.author, request.user))
        context.update(check_bookmark(request.user, recipe))
    return render(request, "recipe_page.html", context)


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
        Ingredient.objects.filter(recipe=instance).exclude(
            food__in=ingredients.keys()
        ).delete()
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


@login_required
def follow_view(request):
    user = request.user
    authors = User.objects.filter(following__user=user).order_by(
        "-following__follow_date"
    )
    paginator, page = make_pagination(request, authors, FOLLOW_PAGE_SIZE)
    count_hidden, authors_names, recipes = {}, {}, {}
    for author in page:
        count_hidden[author.id] = author.recipes.count() - FOLLOW_PAGE_SIZE
        if count_hidden[author.id] < 1:
            count_hidden[author.id] = 0
        authors_names[author.id] = get_name(author)["author_name"]
        recipes[author.id] = author.recipes.all()[:RECIPES_FOLLOW_PAGE]
    context = {"paginator": paginator, "page": page}
    context.update({"count_hidden": count_hidden})
    context.update({"authors_names": authors_names})
    context.update({"recipes": recipes})
    # context.update({})
    return render(request, "follow_page.html", context)


def user_view(request, username):
    author = get_object_or_404(User, username=username)
    recipes = author.recipes.all()
    paginator, page = make_pagination(request, recipes, INDEX_PAGE_SIZE)
    context = {"page": page, "paginator": paginator, "tags": Tag.objects.all()}
    context.update({"author": author})
    context.update(get_recipes_tags(page))
    context.update(get_name(author))
    context.update(can_subscribe(author, request.user))
    if request.user.is_authenticated:
        context.update(is_subscribed(author, request.user))
        context.update(recipes_in_bookmarks(request.user, recipes))
    return render(request, "index.html", context)


# def gen_data():
#     with open("names.txt", "r") as file:
#         for f in file:
#             first, last = f.split()
#             username = slugify(f)
#             User.objects.create(
#                 first_name=first, last_name=last, username=username
#             )
