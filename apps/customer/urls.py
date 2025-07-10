from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page_view, name='landing_page'),
    path('set-location/', views.set_location, name='set_location'),
    path('restaurants/nearby/', views.restaurants_nearby_view, name='restaurants_nearby'),
    path('category/<slug:slug>/', views.restaurants_by_category, name='restaurants_by_category'),
    path('restaurant/<slug:slug>/', views.restaurant_detail_view, name='restaurant_detail'),
    path('cart/update/', views.cart_update_view, name='cart_update'),
    path('favorite/', views.favorite_view, name='favorite'),
    # --- Checkout stepper ---
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/payment-method/', views.checkout_payment_method, name='checkout_payment_method'),
    path('checkout/status/<int:order_id>/', views.checkout_status_poll, name='checkout_status_poll'),

    # Order history for Alpine.js drawer/modal (JSON, only for customer)
    path('order-history/json/', views.order_history_json, name='order_history_json'),
    path('review/product/', views.review_product, name='review_product'),
]
