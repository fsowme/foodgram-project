from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.main, name="index"),
    path("<str:recipe_slug>/edit/", views.recipe_edit, name="edit"),
    path("<str:recipe_slug>/delete/", views.delete, name="delete"),
    path("<str:recipe_slug>/", views.recipe_view, name="recipe"),
]
