# customer/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_landing_view, name='customer_landing'),
    path('kategori/<slug:slug>/restoran/', views.restaurants_by_category, name='restaurants_by_category'),
]
