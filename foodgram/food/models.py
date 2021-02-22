from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=20, verbose_name="Имя тэга", unique=True
    )

    def __str__(self):
        return f"Тэг: {self.name}"


class Food(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название продукта")
    unit = models.CharField(max_length=20, verbose_name="Единица измерения")

    class Meta:
        unique_together = ["name", "unit"]

    def __str__(self):
        return f"Продукт: {self.name}"


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
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации рецепта", auto_now_add=True
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return f"Рецепт: {self.name}"


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
        verbose_name="Рецепт ингридиента",
    )

    class Meta:
        unique_together = ["food", "recipe"]

    def __str__(self):
        return (
            f"Продукт {self.food.name}, "
            f"как ингредиент блюда {self.recipe.name}"
        )
