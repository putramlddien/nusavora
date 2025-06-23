# customer/views.py
from django.shortcuts import render, get_object_or_404
from products.models import Category
from restaurants.models import Restaurant

def customer_landing_view(request):
    categories = Category.objects.filter(restaurant__isnull=True)  # kategori global
    return render(request, 'customer/landing_page.html', {'categories': categories})

def restaurants_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    restaurants = Restaurant.objects.filter(product__category=category).distinct()
    return render(request, 'customer/restaurants_by_category.html', {
        'category': category,
        'restaurants': restaurants
    })
