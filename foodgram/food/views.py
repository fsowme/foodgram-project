from io import StringIO

# import pdfkit
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse, response
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import Context
from django.template.loader import get_template
# from reportlab.pdfgen import canvas
from users.models import User

from .forms import RecipeForm
from .models import Bookmark, Follow, Ingredient, Purchase, Recipe, Tag

INDEX_PAGE_SIZE = 6
FOLLOW_PAGE_SIZE = 3
BOOKMARK_PAGE_SIZE = 6
RECIPES_FOLLOW_PAGE = 3
BOOKMARK_PAGE_SIZE = 3


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


def amount_purchases(request):
    if request.user.is_authenticated:
        return {"amount_purchases": request.user.purchases.count()}
    slugs = request.session.keys()
    return {"amount_purchases": Recipe.objects.filter(slug__in=slugs).count()}


def check_purchase(request, recipe):
    if request.user.is_authenticated:
        in_purchase = request.user.purchases.filter(recipe=recipe).exists()
        return {"in_purchase": in_purchase}
    return {"in_purchase": bool(recipe.slug in request.session.keys())}


def recipes_in_purchases(request, recipes):
    if request.user.is_authenticated:
        purchases = {
            _.id: check_purchase(request, _)["in_purchase"] for _ in recipes
        }
        return {"purchases": purchases}
    slugs = request.session.keys()
    purchases = {_.id: str(_.slug) in slugs for _ in recipes}
    return {"purchases": purchases}


def filter_by_tags(request, queryset):
    tags = request.GET.get("tag")
    return queryset.objects.filter(tag__eng_name__in=tags).distinct()


def main(request):
    recipes = Recipe.objects.all()
    paginator, page = make_pagination(request, recipes, INDEX_PAGE_SIZE)
    context = {"page": page, "paginator": paginator, "tags": Tag.objects.all()}
    context.update(get_recipes_tags(page))
    context.update(get_authors(page))
    context.update(get_authors_names(page))
    context.update(recipes_in_purchases(request, page))
    context.update(amount_purchases(request))
    context.update(recipes_in_bookmarks(request.user, page))
    return render(request, "index.html", context)


def user_view(request, username):
    author = get_object_or_404(User, username=username)
    recipes = author.recipes.all()
    paginator, page = make_pagination(request, recipes, INDEX_PAGE_SIZE)
    context = {"page": page, "paginator": paginator, "tags": Tag.objects.all()}
    context.update({"author": author})
    context.update(get_recipes_tags(page))
    context.update(get_name(author))
    context.update(recipes_in_purchases(request, page))
    context.update(amount_purchases(request))
    if request.user.is_authenticated:
        context.update(can_subscribe(author, request.user))
        context.update(recipes_in_bookmarks(request.user, page))
        context.update(is_subscribed(author, request.user))
    print(context)
    return render(request, "index.html", context)


@login_required
def bookmark_view(request):
    user = request.user
    recipes = Recipe.objects.filter(in_bookmark__user=user)
    paginator, page = make_pagination(request, recipes, BOOKMARK_PAGE_SIZE)
    context = {"paginator": paginator, "page": page, "tags": Tag.objects.all()}
    context.update(get_recipes_tags(page))
    context.update(get_authors(page))
    context.update(get_authors_names(page))
    context.update(recipes_in_bookmarks(user, page))
    context.update(recipes_in_purchases(request, page))
    context.update(amount_purchases(request))
    return render(request, "index.html", context)


def recipe_view(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    tags_names = recipe.tag.values("name", "eng_name", "color")
    context = {"recipe": recipe, "tags": tags_names, "author": recipe.author}
    context.update(get_name(recipe.author))
    context.update(is_editable(recipe.author, request.user))
    context.update(can_subscribe(recipe.author, request.user))
    context.update(amount_purchases(request))
    context.update(check_purchase(request, recipe))
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
    context.update(amount_purchases(request))
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


def purchase_view(request, recipe_slug=None, download=None):
    if not request.user.is_authenticated:
        if slugs := request.session.keys():
            if recipe_slug:
                del request.session[recipe_slug]
        recipes = Recipe.objects.filter(slug__in=slugs)
    else:
        if recipe_slug:
            purchase = get_object_or_404(
                Purchase, user=request.user, recipe__slug=recipe_slug
            )
            purchase.delete()
        recipes = Recipe.objects.filter(in_purchases__user=request.user)
    context = {"amount_purchases": recipes.count(), "recipes": recipes}
    if download:
        ingredients = Ingredient.objects.filter(recipe__in=recipes)
        context.update({"shopping": ingredients_list(ingredients)})
        file = StringIO()
        for ingredient in ingredients_list(ingredients):
            print(ingredient)
            file.write(f'{ingredient}\n')
        response = HttpResponse(file.getvalue(),  content_type="application/default")
        response['Content-Disposition'] = 'attachment; filename=ingrs.txt'
        return response


    return render(request, "purchase_page.html", context)


def ingredients_list(ingredients):
    shoppings = {}
    for ingredient in ingredients:
        name, unit = ingredient.food.name, ingredient.food.unit
        amount = ingredient.amount
        if shoppings.get(name):
            if shoppings[name].get(unit, -1) == -1:
                shoppings[name][unit] = amount
            elif amount is not None:
                shoppings[name][unit] += amount
            else:
                shoppings[name][unit] = amount
        else:
            shoppings[name] = {unit: amount}
    shoppings_list = []
    for food in shoppings:
        for unit in shoppings[food]:
            if shoppings[food][unit]:
                shoppings_list.append(f"{food} {shoppings[food][unit]} {unit}")
            else:
                shoppings_list.append(f"{food} {unit}")
    return shoppings_list
