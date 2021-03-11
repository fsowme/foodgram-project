import uuid

from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=20, unique=True, verbose_name="Имя тэга"
    )
    eng_name = models.CharField(
        max_length=20, unique=True, verbose_name="Tag name"
    )
    color = models.CharField(
        max_length=100, unique=True, verbose_name="Цвет тэга"
    )

    def __str__(self):
        return self.name


class Food(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название продукта")
    unit = models.CharField(max_length=20, verbose_name="Единица измерения")
    counted = models.BooleanField(blank=False, null=False, default=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "unit"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название рецепта")
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Рецепты автора",
    )
    image = models.ImageField(
        verbose_name="Картинка рецепта", upload_to="food/"
    )
    description = models.TextField(verbose_name="Описание рецепта")
    tag = models.ManyToManyField(to=Tag, related_name="recipes")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах"
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации рецепта", auto_now_add=True
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


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
    amount = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Количество ингредиента",
    )

    class Meta:
        ordering = ["recipe"]
        unique_together = ["food", "recipe"]

    def save(self, *args, **kwargs):
        if not self.food.counted:
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
    follow_date = models.DateTimeField(
        verbose_name="Дата публикации рецепта", auto_now_add=True
    )

    class Meta:
        ordering = ["-follow_date"]
        unique_together = ["user", "author"]
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_check_self_follow",
                check=~models.Q(user=models.F("author")),
            )
        ]

    def __str__(self):
        return f"Подписка {self.user.username} на {self.author.username}"


class Bookmark(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bookmarks"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="in_bookmark"
    )

    class Meta:
        unique_together = ["user", "recipe"]

    def __str__(self):
        return (
            f"Закладка рецепта {self.recipe.name} "
            f"у автора {self.user.username}"
        )


class Purchase(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="purchases"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="in_purchases"
    )

    class Meta:
        unique_together = ["user", "recipe"]

    def __str__(self):
        return f"{self.recipe.name} как покупка у {self.user.username}"
