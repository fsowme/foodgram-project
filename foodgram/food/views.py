from django.core.paginator import Paginator
from django.shortcuts import HttpResponse, get_object_or_404, render

from .models import Recipe, Tag, User


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


def get_human_time(time):
    human_time = ""
    human_time += f"{time.hour} ч." if time.hour else ""
    human_time += f" {time.minute} мин." if time.minute else ""
    human_time += f" {time.second} сек." if time.second else ""
    return {"human_time": human_time}


def get_fullname_or_username(user):
    if user.first_name and user.last_name:
        return {"author_name": f"{user.first_name} {user.last_name}"}
    return {"author_name": f"{user.username}"}


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
    context.update(get_human_time(recipe.cooking_time))
    context.update(get_fullname_or_username(recipe.author))
    return render(request, "singlePage.html", context)


def recipe_edit(request, recipe_slug):
    return HttpResponse("OK")
