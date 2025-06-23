# customer/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from products.models import Category
from restaurants.models import Restaurant
from core.utils import haversine
from products.models import Product
from django.contrib.auth.decorators import login_required
import json

def landing_page_view(request):
    categories = Category.objects.filter(is_global=True)
    location = request.session.get('location', None)
    return render(request, 'customer/landing_page.html', {
        'categories': categories,
        'location': location,
    })

def set_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['location'] = {
            'address': data.get('address'),
            'lat': data.get('lat'),
            'lng': data.get('lng'),
        }
        # Setelah set lokasi, redirect ke nearby restaurants
        return JsonResponse({'status': 'ok', 'redirect': '/restaurants/nearby/'})
    return JsonResponse({'error': 'Invalid method'}, status=400)

def restaurants_nearby_view(request):
    location = request.session.get('location')
    if not location:
        return redirect('landing_page')
    lat, lng = float(location['lat']), float(location['lng'])
    # Ambil semua restoran yang punya latitude/longitude
    restaurants = Restaurant.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    nearby = []
    for r in restaurants:
        if r.latitude and r.longitude:
            dist = haversine(lat, lng, r.latitude, r.longitude)
            if dist <= 20:
                r.distance = round(dist, 2)
                nearby.append(r)
    return render(request, 'customer/restaurants_nearby.html', {
        'restaurants': sorted(nearby, key=lambda x: x.distance),
        'location': location,
    })

def restaurants_by_category(request, slug):
    location = request.session.get('location')
    if not location:
        return redirect('landing_page_view')
    lat, lng = float(location['lat']), float(location['lng'])
    category = get_object_or_404(Category, slug=slug)
    restaurants = Restaurant.objects.filter(products__category=category).exclude(latitude__isnull=True).exclude(longitude__isnull=True).distinct()
    nearby = []
    for r in restaurants:
        if r.latitude and r.longitude:
            dist = haversine(lat, lng, r.latitude, r.longitude)
            if dist <= 20:
                r.distance = round(dist, 2)
                nearby.append(r)
    return render(request, 'customer/restaurants_by_category.html', {
        'category': category,
        'restaurants': sorted(nearby, key=lambda x: x.distance),
        'location': location,
    })

@login_required
def cart_update_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        product_id = data.get('product_id')
        qty = data.get('qty', 1)
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product, is_active=True)
        if action == 'add':
            cart_item.qty += qty
            cart_item.save()
        elif action == 'remove':
            cart_item.delete()
        elif action == 'update':
            cart_item.qty = qty
            cart_item.save()
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        total = sum(item.product.price * item.qty for item in cart_items)
        return JsonResponse({'status': 'ok', 'cartCount': cart_items.count(), 'totalPrice': total})
    return JsonResponse({'error': 'Invalid method'}, status=400)

@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:20]
    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'created_at': order.created_at.strftime('%d %b %Y %H:%M'),
            'status': order.status,
            'payment_status': order.payment_status,
            'items': [{'menu': item.product.name, 'qty': item.qty} for item in order.items.all()]
        })
    return JsonResponse({'orders': data})

@login_required
def favorite_view(request):
    if request.method == 'GET':
        favorites = request.user.favorites.all()
        data = [{
            'id': fav.id,
            'name': fav.name,
            'price': fav.price,
            'image': fav.image.url if fav.image else ''
        } for fav in favorites]
        return JsonResponse({'favorites': data})
    elif request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        if product in request.user.favorites.all():
            request.user.favorites.remove(product)
            status = 'removed'
        else:
            request.user.favorites.add(product)
            status = 'added'
        return JsonResponse({'status': status})
    return JsonResponse({'error': 'Invalid method'}, status=400)

def restaurant_detail_view(request, slug):
    location = request.session.get('location')
    restaurant = get_object_or_404(Restaurant, slug=slug)
    distance = None
    if location and restaurant.latitude and restaurant.longitude:
        distance = round(haversine(float(location['lat']), float(location['lng']), restaurant.latitude, restaurant.longitude), 2)
    products = Product.objects.filter(restaurant=restaurant)
    return render(request, 'customer/restaurant_detail.html', {
        'restaurant': restaurant,
        'products': products,
        'distance': distance,
    })
