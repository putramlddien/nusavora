from django.urls import path, include
from .views import dashboard_view, restaurant_profile_view

urlpatterns = [
    path('dashboard/', dashboard_view, name='merchant_dashboard'),
    path('profile/', restaurant_profile_view, name='restaurant_profile'),
]
