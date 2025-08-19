from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .algorithms import model_based
from products.models import Product
from reviews.models import Review
from restaurants.models import Restaurant
from django.db.models import Avg, Count
from .models import RecommendationCache

@login_required
def rekomendasi_produk(request):
    user = request.user
    top_k = int(request.GET.get('top_k', 5))

    # Gunakan cache jika tersedia
    cached = RecommendationCache.objects.filter(user=user).order_by('-score')[:top_k]
    if cached.exists():
        result = [(c.product.id, c.score) for c in cached]
    else:
        # Coba model_based
        result = []
        try:
            svd_result = model_based.get_recommendations(user.id, top_k=top_k*3)  # ambil lebih banyak untuk filter
            user_location = request.session.get('location')
            if user_location:
                from core.utils import haversine
                user_lat, user_lng = float(user_location['lat']), float(user_location['lng'])
                filtered = []
                for pid, score in svd_result:
                    try:
                        prod = Product.objects.select_related('restaurant').get(id=pid)
                        resto = prod.restaurant
                        if resto and resto.latitude and resto.longitude:
                            dist = haversine(user_lat, user_lng, resto.latitude, resto.longitude)
                            if dist <= 20:
                                filtered.append((pid, score))
                        if len(filtered) >= top_k:
                            break
                    except Product.DoesNotExist:
                        continue
                result = filtered[:top_k]
            else:
                result = svd_result[:top_k]
        except Exception:
            result = []

    # Jika tetap kosong, fallback ke produk populer di daerah user
    if not result:
        user_location = request.session.get('location')
        if user_location:
            from core.utils import haversine
            user_lat, user_lng = float(user_location['lat']), float(user_location['lng'])
            # Cari restoran terdekat (misal radius 20km)
            nearby_restos = []
            for resto in Restaurant.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True):
                if resto.latitude and resto.longitude:
                    dist = haversine(user_lat, user_lng, resto.latitude, resto.longitude)
                    if dist <= 20:
                        nearby_restos.append(resto.id)
            # Cari produk terlaris di restoran terdekat
            from orders.models import OrderItem
            populer = (
                OrderItem.objects.filter(product__restaurant_id__in=nearby_restos)
                .values('product')
                .annotate(total=Count('id'))
                .order_by('-total')[:top_k]
            )
            product_ids = [p['product'] for p in populer]
            result = [(pid, 0) for pid in product_ids]
        else:
            # Jika tidak ada lokasi, fallback ke produk terlaris global
            from orders.models import OrderItem
            populer = (
                OrderItem.objects.values('product')
                .annotate(total=Count('id'))
                .order_by('-total')[:top_k]
            )
            product_ids = [p['product'] for p in populer]
            result = [(pid, 0) for pid in product_ids]
    else:
        product_ids = [item_id for item_id, _ in result]

    products_qs = Product.objects.filter(id__in=[item_id for item_id, _ in result]).select_related('restaurant', 'category')

    ratings = Review.objects.filter(
        object_id__in=[item_id for item_id, _ in result], is_approved=True
    ).values('object_id').annotate(avg_rating=Avg('rating'))
    avg_rating_map = {r['object_id']: r['avg_rating'] for r in ratings}

    user_location = request.session.get('location')
    resto_distance_map = {}
    if user_location:
        from core.utils import haversine
        user_lat, user_lng = float(user_location['lat']), float(user_location['lng'])
        for prod in products_qs:
            resto = prod.restaurant
            if resto and resto.latitude and resto.longitude:
                dist = haversine(user_lat, user_lng, resto.latitude, resto.longitude)
                resto_distance_map[resto.id] = round(dist, 2)

    score_map = {item_id: score for item_id, score in result}
    products = []
    for prod in products_qs:
        products.append({
            'id': prod.id,
            'name': prod.name,
            'score': round(float(score_map.get(prod.id, 0)), 3),
            'image': prod.image.url if prod.image else None,
            'price': int(prod.price) if hasattr(prod, 'price') and prod.price is not None else None,
            'category': prod.category.name if getattr(prod, 'category', None) else '',
            'restaurant_name': prod.restaurant.name if prod.restaurant else '',
            'restaurant_id': prod.restaurant.id if prod.restaurant else None,
            'restaurant_slug': prod.restaurant.slug if prod.restaurant else '',
            'avg_rating': round(avg_rating_map.get(prod.id, 0), 1) if avg_rating_map.get(prod.id, 0) else None,
            'distance': resto_distance_map.get(prod.restaurant.id) if prod.restaurant else None,
            'is_best_seller': getattr(prod, 'is_best_seller', False),
        })
    return JsonResponse({'user': user.id, 'recommendations': products})
