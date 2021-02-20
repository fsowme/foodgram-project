from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=20, verbose_name="Имя тэга", unique=True
    )


class Food(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="Название ингредиента"
    )
    unit = models.CharField(max_length=20, verbose_name="Единица измерения")

    class Meta:
        unique_together = ["name", "unit"]


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название рецепта")
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Рецепты автора",
    )
    iamge = models.ImageField(verbose_name="Картинка рецепта")
    description = models.TextField(verbose_name="Описание рецепта")
    tag = models.ManyToManyField(
        to=Tag,
    )
    cooking_time = models.TimeField(verbose_name="Время приготовления")


class Ingredient(models.Model):
    amount = models.SmallIntegerField(verbose_name="Количество ингредиента")
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
        verbose_name="Ингредиенты рецепта",
    )

    class Meta:
        unique_together = ["food", "recipe"]
