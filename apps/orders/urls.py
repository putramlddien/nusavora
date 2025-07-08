from django.urls import path
from .views import update_order_process_status, customer_order_status, customer_order_tracking, customer_cancel_order

urlpatterns = [
    path('merchant/order/<int:order_id>/update-status/', update_order_process_status, name='merchant_update_order_status'),
    path('customer/order/<int:order_id>/status/', customer_order_status, name='customer_order_status'),
    path('customer/order/tracking/', customer_order_tracking, name='customer_order_tracking'),
    path('customer/order/<int:order_id>/cancel/', customer_cancel_order, name='customer_cancel_order'),
]
