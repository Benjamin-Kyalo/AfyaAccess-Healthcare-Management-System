from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # show useful contact and role info in admin list view
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "designation",
        "department",
        "phone_number",
        "is_staff",
    )
    search_fields = ("username", "email", "phone_number")
