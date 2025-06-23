from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page_view, name='landing_page'),
    path('set-location/', views.set_location, name='set_location'),
    path('restaurants/nearby/', views.restaurants_nearby_view, name='restaurants_nearby'),
    path('category/<slug:slug>/', views.restaurants_by_category, name='restaurants_by_category'),
    path('restaurant/<slug:slug>/', views.restaurant_detail_view, name='restaurant_detail'),  # Perbaiki trailing slash
    path('cart/update/', views.cart_update_view, name='cart_update'),
    path('order/history/', views.order_history_view, name='order_history'),
    path('favorite/', views.favorite_view, name='favorite'),
]
