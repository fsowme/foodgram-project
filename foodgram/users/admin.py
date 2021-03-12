from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class MyUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name")
    search_fields = ("username", "email")


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
