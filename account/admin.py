from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_premium', 'telegram_chat_id']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('telegram_chat_id', 'is_premium', 'premium_expires_at')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
