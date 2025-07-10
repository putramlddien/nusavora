from django.urls import path
from .views import rekomendasi_produk

urlpatterns = [
    path('api/recommendations/', rekomendasi_produk, name='api_recommendations'),
]