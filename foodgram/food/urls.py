from django.conf.urls import url
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.main, name="index"),
    path("new/", views.recipe_new, name="new"),
    path("bookmark/", views.bookmark_view, name="bookmark"),
    path("follow/", views.follow_view, name="follow"),
    path("purchase/", views.purchase_view, name="purchase"),
    path("purchase/<slug:recipe_slug>/", views.purchase_view, name="purchase"),
    path("author/<str:username>/", views.user_view, name="user"),
    path("<slug:recipe_slug>/edit/", views.recipe_edit, name="edit"),
    path("<slug:recipe_slug>/delete/", views.recipe_delete, name="delete"),
    path("<slug:recipe_slug>/", views.recipe_view, name="recipe"),
]
