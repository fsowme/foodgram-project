from django.core.paginator import Paginator
from django.db.models import Case, CharField, F, Q, When
from django.db.models.expressions import Exists, OuterRef
from django.db.models.fields import BooleanField

from food.models import Bookmark, Follow, Purchase, Recipe, Tag


def make_pagination(request, elements, total_on_page):
    paginator = Paginator(elements, total_on_page)
    page_number = request.GET.get("page", 1)
    page = paginator.get_page(page_number)
    page.object_list
    return paginator, page


def get_authors_names(recipes):
    authors = dict(
        recipes.annotate(
            author_name=Case(
                When(
                    Q(author__first_name="") | Q(author__last_name=""),
                    then=F("author__username"),
                ),
                default="author__first_name",
                output_field=CharField(),
            )
        ).values_list("pk", "author_name")
    )
    return {"authors_names": authors}


def get_authors(recipes):
    authors = dict(recipes.values_list("pk", "author__username"))
    return {"authors": authors}


def get_name(user):
    if user.first_name and user.last_name:
        return {"author_name": f"{user.first_name} {user.last_name}"}
    return {"author_name": f"{user.username}"}


def get_ingredients(recipe):
    ingredients_in_recipe = recipe.ingredients.values(
        "amount", food_name=F("food__name"), food_unit=F("food__unit")
    )
    return {"ingredients": ingredients_in_recipe}


def is_editable(author, user):
    editable = user.is_authenticated and user == author
    return {"can_edit": editable}


def is_subscribed(author, user):
    subscribed = Follow.objects.filter(author=author, user=user).exists()
    return {"subscribed": subscribed}


def can_subscribe(author, user):
    return {"can_subscribe": user.is_authenticated and user != author}


def check_bookmark(user, recipe):
    in_bookmark = (
        user.is_authenticated
        and Bookmark.objects.filter(user=user, recipe=recipe).exists()
    )
    return {"in_bookmark": in_bookmark}


def can_mark(user, recipes):
    can_bookmark = dict(
        recipes.annotate(
            can_mark=Case(
                When(Q(author__pk=user.pk), then=False),
                default=True,
                output_field=BooleanField(),
            )
        ).values_list("pk", "can_mark")
    )
    return {"can_mark": can_bookmark}


def recipes_in_bookmarks(user, recipes):
    bookmarks_subquery = Bookmark.objects.filter(
        recipe=OuterRef("pk"), user__pk=user.pk
    )
    in_bookmarks = dict(
        recipes.annotate(in_bookmarks=Exists(bookmarks_subquery)).values_list(
            "pk", "in_bookmarks"
        )
    )
    return {"bookmarks": in_bookmarks}


def amount_purchases(request):
    if request.user.is_authenticated:
        return {"amount_purchases": request.user.purchases.count()}
    slugs = request.session.keys()
    return {"amount_purchases": Recipe.objects.filter(slug__in=slugs).count()}


def check_purchase(request, recipe):
    if request.user.is_authenticated:
        in_purchase = request.user.purchases.filter(recipe=recipe).exists()
        return {"in_purchase": in_purchase}
    return {"in_purchase": str(recipe.slug) in request.session.keys()}


def recipes_in_purchases(request, recipes):
    if request.user.is_authenticated:
        purchase_subquery = Purchase.objects.filter(
            recipe=OuterRef("pk"), user__pk=request.user.pk
        )
        in_purchase = dict(
            recipes.annotate(
                in_purchase=Exists(purchase_subquery)
            ).values_list("pk", "in_purchase")
        )
        return {"purchases": in_purchase}
    slugs = request.session.keys()
    purchases = dict(
        recipes.annotate(
            in_purchase=Case(
                When(slug__in=slugs, then=True),
                default=False,
                output_field=BooleanField(),
            )
        ).values_list("pk", "in_purchase")
    )
    return {"purchases": purchases}


def filter_by_tags(request, queryset):
    tags = request.GET.getlist("disable")
    tags = Tag.objects.exclude(eng_name__in=tags)
    tags_names = list(tags.values_list("eng_name", flat=True))
    filtered_recipes = queryset.filter(
        tags__eng_name__in=tags_names
    ).distinct()
    return {"disabled_tags": tags_names}, filtered_recipes


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
