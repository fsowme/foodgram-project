from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.main, name="index"),
    path("new/", views.recipe_new, name="new"),
    path("<str:recipe_slug>/edit/", views.recipe_edit, name="edit"),
    path("<str:recipe_slug>/delete/", views.recipe_delete, name="delete"),
    path("<str:recipe_slug>/", views.recipe_view, name="recipe"),
    path("author/<str:username>/", views.user_view, name="user"),
]
