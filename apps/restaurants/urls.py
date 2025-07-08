from django.urls import path, include
from .views import dashboard_view, restaurant_profile_view, orders_active_view, orders_incoming_view, merchant_update_order_status

urlpatterns = [
    path('dashboard/', dashboard_view, name='merchant_dashboard'),
    path('profile/', restaurant_profile_view, name='restaurant_profile'),
    path('orders/active/', orders_active_view, name='merchant_orders_active'),
    path('orders/incoming/', orders_incoming_view, name='merchant_orders_incoming'),
    path('orders/<int:order_id>/update-status/', merchant_update_order_status, name='merchant_update_order_status'),
]
