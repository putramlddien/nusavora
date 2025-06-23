from django.contrib import admin
from .models import Restaurant

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'address', 'is_open']
    list_filter = ['is_open']
    search_fields = ['name', 'address']
    autocomplete_fields = ['owner']
