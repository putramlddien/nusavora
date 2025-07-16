from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from products.models import Category
from restaurants.models import Restaurant
from reviews.models import Review
from django.views.decorators.http import require_POST
from core.utils import haversine
from products.models import Product
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime, time
from orders.models import Cart, CartItem, Order, OrderItem
from orders.services import create_order_from_cart
from django.db import transaction
from django.urls import reverse
from django.core import serializers
from django.contrib.contenttypes.models import ContentType
from customer.models import ProductViewLog, AddToCartLog, PurchaseLog

def landing_page_view(request):
    categories = Category.objects.filter(is_global=True)
    location = request.session.get('location', None)
    return render(request, 'customer/landing_page.html', {
        'categories': categories,
        'location': location,
        'is_landing_page': True,
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
    # Cuma ambil yang ada koordinatnya
    restaurants = Restaurant.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

    resto_list = []
    for r in restaurants:
        if r.latitude and r.longitude:
            dist = haversine(lat, lng, r.latitude, r.longitude)
            if dist <= 20:
                resto_list.append({
                    'instance': r,
                    'distance': round(dist, 2),
                    'avg_rating': r.avg_rating,     # property model
                    'total_reviews': r.total_reviews, # property model
                })

    # Urutkan jarak terdekat
    resto_list = sorted(resto_list, key=lambda x: x['distance'])

    return render(request, 'customer/restaurants_nearby.html', {
        'restaurants': resto_list,
        'location': location,
    })

def restaurants_by_category(request, slug):
    location = request.session.get('location')
    if not location:
        return redirect('landing_page')
    lat, lng = float(location['lat']), float(location['lng'])
    category = get_object_or_404(Category, slug=slug)
    
    # Filter resto yang punya produk di kategori tsb
    restaurants = Restaurant.objects.filter(
        products__category=category
    ).exclude(latitude__isnull=True).exclude(longitude__isnull=True).distinct()

    resto_list = []
    for r in restaurants:
        if r.latitude and r.longitude:
            dist = haversine(lat, lng, r.latitude, r.longitude)
            if dist <= 20:
                resto_list.append({
                    'instance': r,
                    'distance': round(dist, 2),
                    'avg_rating': r.avg_rating,
                    'total_reviews': r.total_reviews,
                    'product_categories': list(r.products.values_list('category__name', flat=True).distinct()),
                    })

    resto_list = sorted(resto_list, key=lambda x: x['distance'])

    return render(request, 'customer/restaurants_by_category.html', {
        'category': category,
        'restaurants': resto_list,
        'location': location,
    })

def get_or_create_cart(request, restaurant):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart and cart.restaurant != restaurant:
            cart.items.all().delete()
            cart.restaurant = restaurant
            cart.save()
        if not cart:
            cart = Cart.objects.create(user=request.user, restaurant=restaurant)
    else:
        session_key = request.session.session_key or request.session.save() or request.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first()
        if cart and cart.restaurant != restaurant:
            cart.items.all().delete()
            cart.restaurant = restaurant
            cart.save()
        if not cart:
            cart = Cart.objects.create(session_key=session_key, restaurant=restaurant)
    return cart

@login_required
def product_detail_json(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Catat event view di sini!
    ProductViewLog.objects.create(user=request.user, product=product)
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': float(product.price),
        'image': product.image.url if product.image else '',
        # Tambahkan info lain jika perlu
    })

@transaction.atomic
@login_required
def cart_update_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        
        # Handle 'get' tanpa product_id
        if action == 'get':
            cart = Cart.objects.filter(user=request.user).first()
            items = [
                {
                    'id': item.product.id,
                    'name': item.product.name,
                    'qty': item.qty,
                    'price': float(item.product.price),
                    'image': item.product.image.url if item.product.image else '',
                } for item in cart.items.all()
            ] if cart else []
            total = sum(item['price'] * item['qty'] for item in items)
            return JsonResponse({'status': 'ok', 'cartCount': sum(i['qty'] for i in items), 'totalPrice': total, 'items': items, 'restaurant_id': cart.restaurant.id if cart else None})
        
        # Selain 'get', baru cek product_id
        product_id = data.get('product_id')
        qty = int(data.get('qty', 1))
        product = get_object_or_404(Product, id=product_id)
        cart = get_or_create_cart(request, product.restaurant)
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        if action == 'add':
            if cart_item:
                cart_item.qty += qty
                cart_item.save()
            else:
                CartItem.objects.create(cart=cart, product=product, qty=qty)
            if request.user.is_authenticated:
                AddToCartLog.objects.create(user=request.user, product=product)
        elif action == 'inc' and cart_item:
            cart_item.qty += 1
            cart_item.save()
        elif action == 'dec' and cart_item:
            if cart_item.qty > 1:
                cart_item.qty -= 1
                cart_item.save()
            else:
                cart_item.delete()
        elif action == 'remove' and cart_item:
            cart_item.delete()
        elif action == 'update' and cart_item:
            cart_item.qty = qty
            cart_item.save()

        # Return cart summary
        items = [
            {
                'id': item.product.id,
                'name': item.product.name,
                'qty': item.qty,
                'price': float(item.product.price),
                'image': item.product.image.url if item.product.image else '',
            } for item in cart.items.all()
        ]
        total = sum(item['price'] * item['qty'] for item in items)
        return JsonResponse({'status': 'ok', 'cartCount': sum(i['qty'] for i in items), 'totalPrice': total, 'items': items, 'restaurant_id': cart.restaurant.id})
    return JsonResponse({'error': 'Invalid method'}, status=400)

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
    # Produk per kategori
    categories = restaurant.products.values('category__id', 'category__name', 'category__slug').distinct()
    category_list = []
    for cat in categories:
        products = restaurant.products.filter(category_id=cat['category__id'])
        category_list.append({
            'id': cat['category__id'],
            'name': cat['category__name'],
            'slug': cat['category__slug'],
            'products': products,
        })

    now = datetime.now().time()  # Local time server

    # Biar aman, parsing ke objek time dulu
    open_time = restaurant.open_time
    close_time = restaurant.close_time

    # Tangani jika jam buka > jam tutup (resto 24 jam/melewati tengah malam)
    is_open = False
    if open_time and close_time:
        if open_time < close_time:
            is_open = open_time <= now < close_time
        else:
            is_open = now >= open_time or now < close_time

    return render(request, 'customer/restaurant_detail.html', {
        'restaurant': restaurant,
        'category_list': category_list,
        'distance': distance,
        'is_open_now': is_open,
        'open_time': open_time.strftime("%H:%M") if open_time else "-",
        'close_time': close_time.strftime("%H:%M") if close_time else "-",
    })

@login_required
def checkout(request):
    # Restore state dari session jika ada order pending
    order_id = request.session.get('checkout_order_id')
    step = request.GET.get('step')
    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            payment = order.payment
            # Cek expired (15 menit dari payment.created_at)
            from datetime import timedelta
            from django.utils import timezone
            expired_at = payment.created_at + timedelta(minutes=15)
            now = timezone.now()
            if order.status == 'waiting_payment':
                if now < expired_at:
                    # Masih dalam window pembayaran, redirect ke instruksi
                    if not step or step == 'summary':
                        return redirect(f'/checkout/?step=instruction&order_id={order_id}')
                else:
                    # Sudah expired, hapus order & payment, reset session
                    try:
                        payment.delete()
                    except Exception:
                        pass
                    try:
                        order.delete()
                    except Exception:
                        pass
                    if 'checkout_order_id' in request.session:
                        del request.session['checkout_order_id']
                    if 'checkout_step' in request.session:
                        del request.session['checkout_step']
            elif order.status in ['expired', 'cancelled']:
                # Hapus order & payment jika status expired/cancelled
                try:
                    payment.delete()
                except Exception:
                    pass
                try:
                    order.delete()
                except Exception:
                    pass
                if 'checkout_order_id' in request.session:
                    del request.session['checkout_order_id']
                if 'checkout_step' in request.session:
                    del request.session['checkout_step']
            # Jika status paid, biarkan saja, JANGAN hapus order/payment
        except Order.DoesNotExist:
            if 'checkout_order_id' in request.session:
                del request.session['checkout_order_id']
            if 'checkout_step' in request.session:
                del request.session['checkout_step']

    step = request.GET.get('step', 'summary')
    context = {'step': step}

    cart = get_object_or_404(Cart, user=request.user)
    cart_total = sum(item.product.price * item.qty for item in cart.items.all())
    
    methods = [
        ('bca_va', 'BCA Virtual Account'), 
        ('bni_va', 'BNI Virtual Account'),
        ('bri_va', 'BRI Virtual Account'), 
        ('permata_va', 'Permata VA'), 
        ('qris', 'QRIS'),
        ('gopay', 'GoPay'),
        ('indomaret', 'Indomaret'), 
        ('alfamart', 'Alfamart')
    ]

    context.update({
        'cart': cart,
        'cart_total': cart_total,
        'methods': methods,
    })

    location = request.session.get('location')
    if location:
        context['location'] = location

    if step == 'instruction':
        order_id = request.GET.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=request.user)
        context.update({'order': order, 'payment': order.payment})

    elif step == 'success':
        order_id = request.GET.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=request.user)
        context['order'] = order

    return render(request, 'customer/checkout.html', context)

@login_required
def checkout_payment_method(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_method = data.get('payment_method')
        delivery_type = data.get('delivery_type', 'pickup')
        delivery_address = data.get('delivery_address', '')
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart kosong. Silakan tambahkan produk ke keranjang.'}, status=400)
        if not cart.items.exists():
            return JsonResponse({'error': 'Cart kosong. Silakan tambahkan produk ke keranjang.'}, status=400)
        # Fallback: jika delivery_type == 'delivery' dan delivery_address kosong, ambil dari session['location']
        if delivery_type == 'delivery' and not delivery_address:
            location = request.session.get('location')
            if location and location.get('address'):
                delivery_address = location['address']
        # Cegah duplikasi order: cek order waiting_payment saja, JANGAN sentuh order paid/expired
        existing_order = Order.objects.filter(user=request.user, status='waiting_payment').first()
        if existing_order:
            payment = existing_order.payment
            # Jika payment lama tidak valid (semua field kosong), hapus order & payment lama, lalu buat baru
            if not (payment.va_number or payment.qr_url or payment.redirect_url or payment.payment_code):
                payment.delete()
                existing_order.delete()
            else:
                response = {
                    'order_id': existing_order.id,
                    'va_number': payment.va_number,
                    'qr_url': payment.qr_url,
                    'redirect_url': payment.redirect_url,
                    'payment_code': payment.payment_code,
                    'method': payment.method,
                    'created_at': payment.created_at.strftime('%Y-%m-%d %H:%M:%S') if payment.created_at else None,
                    'resume': True,
                }
                request.session['checkout_order_id'] = existing_order.id
                request.session['checkout_step'] = 'instruction'
                return JsonResponse(response)
        # Buat order baru jika tidak ada yang pending
        try:
            order, payment, payment_details = create_order_from_cart(
                cart, payment_method, delivery_type, delivery_address
            )
            from customer.models import PurchaseLog
            for item in order.items.all():
                PurchaseLog.objects.create(
                    user=request.user,
                    product=item.product,
                    order=order
                )
            response = {
                'order_id': order.id,
                'va_number': payment.va_number,
                'qr_url': payment.qr_url,
                'redirect_url': payment.redirect_url,
                'payment_code': payment.payment_code,
                'method': payment.method,
                'created_at': payment.created_at.strftime('%Y-%m-%d %H:%M:%S') if payment.created_at else None,
                'resume': False,
            }
            # Jika semua field kosong, kirim error detail ke FE
            if not (payment.va_number or payment.qr_url or payment.redirect_url or payment.payment_code):
                return JsonResponse({'error': 'Metode pembayaran tidak tersedia atau terjadi kesalahan pada Midtrans.', 'midtrans_debug': getattr(payment, 'midtrans_debug', None)}, status=400)
            request.session['checkout_order_id'] = order.id
            request.session['checkout_step'] = 'instruction'
            return JsonResponse(response)
        except Exception as e:
            import traceback
            return JsonResponse({'error': f'Gagal membuat pembayaran: {str(e)}', 'trace': traceback.format_exc()}, status=400)
    
@login_required
def checkout_status_poll(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = order.payment
    # 15 menit expired
    expired_at = payment.created_at.timestamp() + 15*60 if payment.created_at else None
    return JsonResponse({
        'status': payment.status,
        'order_status': order.status,
        'va_number': payment.va_number,
        'qr_url': payment.qr_url,
        'redirect_url': payment.redirect_url,
        'payment_code': payment.payment_code,
        'payment_method': payment.method,
        'created_at': payment.created_at.strftime('%Y-%m-%d %H:%M:%S') if payment.created_at else None,
        'expired_at': expired_at,
    })

@login_required
def order_history_json(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related('items__product', 'restaurant')
        .order_by('-created_at')
    )
    product_ct = ContentType.objects.get_for_model(Product)
    data = []
    for o in orders:
        data.append({
            "id": o.id,
            "created_at": o.created_at.strftime('%Y-%m-%d %H:%M'),
            "status": o.status,
            "payment_status": getattr(o, 'payment_status', None) or (o.payment.status if hasattr(o, 'payment') else None),
            "restaurant": o.restaurant.name if o.restaurant else None,
            "items": [
                {
                    "menu": item.product.name,
                    "product_id": item.product.id,
                    "qty": item.qty,
                    "price": float(item.product.price),
                    "review": (
                        lambda rv: {
                            "rating": rv.rating,
                            "comment": rv.comment,
                            "created_at": rv.created_at.strftime('%d-%m-%Y %H:%M'),
                            "username": rv.user.full_name,
                        } if rv else None
                    )(
                        Review.objects.filter(
                            content_type=product_ct,
                            object_id=item.product.id,
                            user=request.user,
                            is_approved=True
                        ).first()
                    ),
                }
                for item in o.items.all()
            ],
            "total_price": float(o.total_price),
            "payment_method": getattr(o, 'payment_method', None) or (o.payment.method if hasattr(o, 'payment') else None),
            "address": o.address if hasattr(o, 'address') else None,
        })
    return JsonResponse({'orders': data})

@require_POST
@login_required
def review_product(request):
    order_id = request.POST.get('order_id')
    product_id = request.POST.get('product_id')
    rating = int(request.POST.get('rating', 0))
    comment = request.POST.get('comment', '').strip()

    # Validasi order
    try:
        order = Order.objects.get(id=order_id, user=request.user, status='paid')
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order tidak valid'}, status=400)

    # Validasi orderitem (produk tsb memang dibeli dalam order ini)
    try:
        order_item = OrderItem.objects.get(order=order, product_id=product_id)
    except OrderItem.DoesNotExist:
        return JsonResponse({'error': 'Produk tidak ditemukan di order'}, status=400)

    product = order_item.product
    content_type = ContentType.objects.get_for_model(Product)

    # Pastikan belum review produk INI di order INI
    already = Review.objects.filter(
        user=request.user,
        content_type=content_type,
        object_id=product.id,
        # optionally: you can filter by order too, if you want review per order!
    ).exists()
    if already:
        return JsonResponse({'error': 'Kamu sudah mereview produk ini.'}, status=400)

    review = Review.objects.create(
        user=request.user,
        content_type=content_type,
        object_id=product.id,
        rating=rating,
        comment=comment,
        is_approved=True
    )
    return JsonResponse({
        'status': 'ok',
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at.strftime('%d-%m-%Y %H:%M'),
        'username': request.user.full_name,
    })
