from django.urls import path

from apps.customer import views
from .views import rekomendasi_produk, rekomendasi_resto

urlpatterns = [
    path('api/recommendations/', rekomendasi_produk, name='api_recommendations'),
    path('api/recommended-restaurants/', rekomendasi_resto, name='api_recommended_restaurants'),
]