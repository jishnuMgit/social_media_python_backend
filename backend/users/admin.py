from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Follow


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "phone",
        "created_at",
    )

    search_fields = (
        "username",
        "email",
        "phone",
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "follower",
        "following",
        "created_at",
    )

    search_fields = (
        "follower__username",
        "following__username",
    )