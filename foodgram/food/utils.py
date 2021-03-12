from django.core.paginator import Paginator
from food.models import Bookmark, Follow, Recipe, Tag


def make_pagination(request, elements, total_on_page):
    paginator = Paginator(elements, total_on_page)
    page_number = request.GET.get("page", 1)
    page = paginator.get_page(page_number)
    page.object_list
    return paginator, page


def get_recipes_tags(recipes):
    recipes_tags = {}
    tags_on_recipes = recipes.object_list.values_list(
        "pk", "tags__name", "tags__color"
    )
    for recipe_pk, tag_name, tag_color in tags_on_recipes:
        if recipes_tags.get("recipe_pk"):
            recipes_tags[recipe_pk].append([tag_name, tag_color])
        else:
            recipes_tags[recipe_pk] = [tag_name, tag_color]
    print(recipes_tags)
    return {"recipes_tags": recipes_tags}


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


def can_mark(user, recipes):
    return {"can_mark": {_.id: bool(user != _.author) for _ in recipes}}


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
    tags = request.GET.getlist("disable")
    tags = Tag.objects.exclude(eng_name__in=tags)
    tags_names = list(tags.values_list("eng_name", flat=True))
    filtered_recipes = queryset.filter(
        tags__eng_name__in=tags_names
    ).distinct()
    return {"disabled_tags": tags_names}, filtered_recipes
