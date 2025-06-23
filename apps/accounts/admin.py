from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import NusavoraUser, EmailOTP

class NusavoraUserAdmin(UserAdmin):
    model = NusavoraUser
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_staff')
    search_fields = ('email',)
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'full_name', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(NusavoraUser, NusavoraUserAdmin)
admin.site.register(EmailOTP)
