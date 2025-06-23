from django.urls import path
from .views import register_view, verify_otp_view, login_view, logout_view

urlpatterns = [
    path('register/', register_view, name='customer_register'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),
    path('login/', login_view, name='customer_login'),
    path('logout/', logout_view, name='logout'),
]
