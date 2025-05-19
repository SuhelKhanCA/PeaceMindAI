from django.contrib import admin
from users import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
# Register your models here.

@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ( "password",)}),
        (_("Personal Info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("permissions"),
            {
                "fields":(
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "dob")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("pk",)