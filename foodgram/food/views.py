from io import StringIO

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from food.forms import RecipeForm
from food.models import Ingredient, Recipe, Tag
from food.utils import (
    amount_purchases,
    can_mark,
    can_subscribe,
    check_bookmark,
    check_purchase,
    filter_by_tags,
    get_authors,
    get_authors_names,
    get_ingredients,
    get_name,
    ingredients_list,
    is_editable,
    is_subscribed,
    make_pagination,
    recipes_in_bookmarks,
    recipes_in_purchases,
)
from users.models import User

INDEX_PAGE_SIZE = 6
FOLLOW_PAGE_SIZE = 3
BOOKMARK_PAGE_SIZE = 6
RECIPES_FOLLOW_PAGE = 3
BOOKMARK_PAGE_SIZE = 3


def main(request):
    disabled_tags, recipes = filter_by_tags(request, Recipe.objects.all())
    paginator, page = make_pagination(request, recipes, INDEX_PAGE_SIZE)
    context = {"page": page, "paginator": paginator, "tags": Tag.objects.all()}
    context.update(get_authors_names(page.object_list))
    context.update(get_authors(page.object_list))
    context.update(can_mark(request.user, page.object_list))
    context.update(recipes_in_bookmarks(request.user, page.object_list))
    context.update(recipes_in_purchases(request, page.object_list))
    context.update(amount_purchases(request))
    context.update(disabled_tags)

    return render(request, "index.html", context)


def user_view(request, username):
    author = get_object_or_404(User, username=username)
    disabled_tags, recipes = filter_by_tags(request, author.recipes.all())
    paginator, page = make_pagination(request, recipes, INDEX_PAGE_SIZE)
    context = {"page": page, "paginator": paginator, "tags": Tag.objects.all()}
    context.update(can_mark(request.user, page.object_list))
    context.update(disabled_tags)
    context.update({"author": author})
    context.update(get_name(author))
    context.update(amount_purchases(request))
    if request.user.is_authenticated:
        context.update(can_subscribe(author, request.user))
        context.update(recipes_in_bookmarks(request.user, page.object_list))
        context.update(is_subscribed(author, request.user))
    context.update(recipes_in_purchases(request, page.object_list))
    return render(request, "index.html", context)


@login_required
def bookmark_view(request):
    recipes = Recipe.objects.filter(in_bookmark__user=request.user)
    disabled_tags, recipes = filter_by_tags(request, recipes)
    paginator, page = make_pagination(request, recipes, BOOKMARK_PAGE_SIZE)
    context = {"paginator": paginator, "page": page, "tags": Tag.objects.all()}
    context.update(get_authors_names(page.object_list))
    context.update(get_authors(page.object_list))
    context.update(can_mark(request.user, page.object_list))
    context.update(disabled_tags)
    context.update(recipes_in_bookmarks(request.user, page.object_list))
    context.update(recipes_in_purchases(request, page.object_list))
    context.update(amount_purchases(request))
    return render(request, "index.html", context)


def recipe_view(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    tags_names = recipe.tags.values("name", "eng_name", "color")
    context = {"recipe": recipe, "tags": tags_names, "author": recipe.author}
    context.update(get_name(recipe.author))
    context.update(is_editable(recipe.author, request.user))
    context.update(can_subscribe(recipe.author, request.user))
    context.update(amount_purchases(request))
    context.update(check_purchase(request, recipe))
    if request.user.is_authenticated:
        context.update({"can_mark": recipe.author != request.user})
        context.update(is_subscribed(recipe.author, request.user))
        context.update(check_bookmark(request.user, recipe))
    return render(request, "recipe_page.html", context)


@login_required
def recipe_edit(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    if request.user != recipe.author:
        return redirect("recipe", recipe_slug=recipe_slug)
    recipe_form = RecipeForm(
        request.POST or None,
        files=request.FILES or None,
        instance=recipe,
        initial={"author": request.user},
    )
    if recipe_form.is_valid():
        recipe_form.save()
        return redirect("recipe", recipe_slug=recipe_slug)
    context = {"form": recipe_form, "tags": Tag.objects.all()}
    context.update(amount_purchases(request))
    context.update(get_ingredients(recipe))
    return render(request, "recipe_edit_page.html", context)


@login_required
def recipe_new(request):
    recipe_form = RecipeForm(
        request.POST or None,
        files=request.FILES or None,
        initial={"author": request.user},
    )
    if recipe_form.is_valid():
        recipe_form.save()
        return redirect("index")
    context = {"form": recipe_form, "tags": Tag.objects.all()}
    context.update(amount_purchases(request))
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
    context.update(amount_purchases(request))
    return render(request, "follow_page.html", context)


def purchase_view(request, recipe_slug=None, shopping=None):
    if not request.user.is_authenticated:
        if request.session.keys() and recipe_slug:
            del request.session[recipe_slug]
            return redirect("purchase")
        recipes = Recipe.objects.filter(slug__in=request.session.keys())
    else:
        recipes = Recipe.objects.filter(in_purchases__user=request.user)
    context = {"amount_purchases": recipes.count(), "recipes": recipes}
    if shopping:
        ingredients = Ingredient.objects.filter(recipe__in=recipes)
        file = StringIO()
        for ingredient in ingredients_list(ingredients):
            file.write(f"{ingredient}\n")
        response = HttpResponse(
            file.getvalue(), content_type="application/default"
        )
        response["Content-Disposition"] = "attachment; filename=ingrs.txt"
        return response
    return render(request, "purchase_page.html", context)
