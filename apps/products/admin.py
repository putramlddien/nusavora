from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant']
    list_filter = ['restaurant']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'restaurant', 'price', 'is_available', 'is_customizable']
    list_filter = ['category', 'restaurant', 'is_available']
    search_fields = ['name', 'description']
    autocomplete_fields = ['category', 'restaurant']
