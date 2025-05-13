from django.contrib import admin
from django.urls import path
from app.views import home, set_location, get_location, category, cart, product, get_vendors_by_location

urlpatterns = [
    path('', home, name="home"),
    path('set-location/', set_location, name="set_location"),
    path('get-location/', get_location, name="get_location"),
    path("get-vendors/", get_vendors_by_location, name="get_vendors"),
    path('category/', category, name="category"),
    path('product/', product, name="product"),
    path('cart/', cart, name="cart"),
]