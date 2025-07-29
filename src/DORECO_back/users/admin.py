from django.contrib import admin
from .models import CustomUser, Role


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'surnames', 'role', 'is_active', 'is_staff', 'created_at', 'token_status']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'name', 'surnames', 'username']
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'token_status']
    ordering = ['-created_at']
    
    def token_status(self, obj):
        if obj.token and obj.token_expires_at:
            if obj.is_token_valid():
                return "Token válido"
            else:
                return "Token expirado"
        return "Sin token"
    token_status.short_description = 'Estado del Token'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
