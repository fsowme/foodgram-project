from uuid import uuid4

from django.db import models
from django.utils.text import slugify
from users.models import User


def short_uuid():
    uuid = uuid4().hex[:16]
    return uuid


class Tag(models.Model):
    name = models.CharField(
        max_length=20, unique=True, verbose_name="Имя тэга"
    )

    def __str__(self):
        return f"Тэг - {self.name}"


class Food(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название продукта")
    unit = models.CharField(max_length=20, verbose_name="Единица измерения")

    class Meta:
        unique_together = ["name", "unit"]

    def __str__(self):
        return f"Продукт - {self.name}"


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название рецепта")
    slug = models.SlugField(
        default=short_uuid,
        unique=True,
        editable=False,
        verbose_name="Уникальный адрес",
        max_length=220,
    )
    slug_id = models.PositiveSmallIntegerField(
        editable=False, verbose_name="Уникальная чать адреса"
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Рецепты автора",
    )
    image = models.ImageField(verbose_name="Картинка рецепта")
    description = models.TextField(verbose_name="Описание рецепта")
    tag = models.ManyToManyField(to=Tag, related_name="recipes")
    cooking_time = models.TimeField(verbose_name="Время приготовления")
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации рецепта", auto_now_add=True
    )

    def save(self, *args, **kwargs):
        if self.slug_id is None:
            slug = slugify(self.name)
            if twins := Recipe.objects.filter(name=self.name):
                self.slug_id = twins.first().slug_id + 1
                self.slug = f"{slug}_{self.slug_id}"
            else:
                self.slug, self.slug_id = slug, 0
        super(Recipe, self).save(*args, **kwargs)

    class Meta:
        ordering = ["-pub_date"]
        unique_together = ["name", "slug_id"]

    def __str__(self):
        return f"Рецепт - {self.name}"


class Ingredient(models.Model):
    food = models.ForeignKey(
        to=Food,
        on_delete=models.PROTECT,
        related_name="ingredients",
        verbose_name="Продукт как ингредиент",
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="Рецепт ингридиента",
    )
    amount = models.SmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Количество ингредиента",
    )

    class Meta:
        unique_together = ["food", "recipe"]

    def save(self, *args, **kwargs):
        if self.food.unit == "по вкусу":
            self.amount = None
        super(Ingredient, self).save(*args, **kwargs)

    def __str__(self):
        return (
            f"Продукт {self.food.name}, "
            f"как ингредиент блюда {self.recipe.name}"
        )


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )

    class Meta:
        unique_together = ["user", "author"]
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_check_self_follow",
                check=~models.Q(user=models.F("author")),
            )
        ]
