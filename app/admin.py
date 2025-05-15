from django.contrib import admin
from .models import Vendor, Product, Category

@admin.register(Category)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    search_fields = ('name', 'image')

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'kabupaten_kota', 'kecamatan', 'kelurahan', 'latitude', 'longitude')
    search_fields = ('name', 'kabupaten_kota', 'kecamatan')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'category', 'price')
    search_fields = ('name', 'vendor__name', 'category__name', 'price')