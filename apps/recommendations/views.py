from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .algorithms import user_based, item_based
from products.models import Product

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
    products = []
    for item_id, score in result:
        try:
            prod = Product.objects.get(id=item_id)
            products.append({'id': prod.id, 'name': prod.name, 'score': round(float(score), 3)})
        except Product.DoesNotExist:
            continue
    return JsonResponse({'user': user.id, 'recommendations': products})
