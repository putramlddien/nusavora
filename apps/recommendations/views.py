from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .algorithms import user_based, item_based
from products.models import Product
from reviews.models import Review
from restaurants.models import Restaurant
from django.db.models import Avg

@login_required
def rekomendasi_produk(request):
    user = request.user
    metode = request.GET.get('metode', 'user')  # 'user' atau 'item'
    top_k = int(request.GET.get('top_k', 5))

    if metode == 'item':
        result = item_based.get_recommendations(user.id, top_k=top_k)
    else:
        result = user_based.get_recommendations(user.id, top_k=top_k)
    # Ambil info produk
    product_ids = [item_id for item_id, _ in result]
    # Ambil semua sekalian, biar nggak query satu-satu
    products_qs = Product.objects.filter(id__in=product_ids).select_related('restaurant', 'category')

    # Ambil rating rata-rata per produk
    ratings = Review.objects.filter(
        object_id__in=product_ids, is_approved=True
    ).values('object_id').annotate(avg_rating=Avg('rating'))
    avg_rating_map = {r['object_id']: r['avg_rating'] for r in ratings}

    # Optionally: hitung distance dari session location user (kalau mau, misal simpan di session)
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

    # Ambil skor dari hasil algoritma
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
            'is_best_seller': getattr(prod, 'is_best_seller', False), # ganti sesuai field di model
            # Tambah badge atau diskon kalau ada
        })
    return JsonResponse({'user': user.id, 'recommendations': products})

@login_required
def rekomendasi_resto(request):
    user = request.user
    # Ambil produk dari rekomendasi
    result = user_based.get_recommendations(user.id, top_k=20)
    product_ids = [item_id for item_id, _ in result]
    product_qs = Product.objects.filter(id__in=product_ids).select_related('restaurant')

    # Unique resto dari produk rekomendasi
    resto_ids_from_reco = list(product_qs.values_list('restaurant__id', flat=True).distinct())
    restos_from_reco = Restaurant.objects.filter(id__in=resto_ids_from_reco)

    # Ambil resto terdekat dari lokasi (jika user pilih lokasi)
    location = request.session.get('location')
    restos_nearby = Restaurant.objects.none()
    if location:
        from core.utils import haversine
        lat, lng = float(location['lat']), float(location['lng'])
        all_restos = Restaurant.objects.exclude(latitude__isnull=True, longitude__isnull=True)
        restos_with_dist = []
        for r in all_restos:
            if r.latitude and r.longitude:
                dist = haversine(lat, lng, r.latitude, r.longitude)
                if dist <= 20:
                    restos_with_dist.append((r, dist))
        # Urutkan jarak, ambil top 10
        restos_nearby = [x[0] for x in sorted(restos_with_dist, key=lambda x: x[1])[:10]]

    # Gabung unik
    resto_list = []
    resto_ids_seen = set()
    for r in list(restos_from_reco) + list(restos_nearby):
        if r.id not in resto_ids_seen:
            avg_rating = Review.objects.filter(object_id__in=r.products.values_list('id', flat=True), is_approved=True).aggregate(avg=Avg('rating'))['avg']
            resto_list.append({
                'id': r.id,
                'name': r.name,
                'slug': r.slug,
                'image': r.image.url if getattr(r, 'image', None) else None,
                'avg_rating': round(avg_rating or 0, 1),
                'distance': getattr(r, 'distance', None),
                'is_best_seller': getattr(r, 'is_best_seller', False),
                'description': r.description if hasattr(r, 'description') else '',
            })
            resto_ids_seen.add(r.id)

    return JsonResponse({'recommendations': resto_list[:12]})  # Batasin 12 resto saja
