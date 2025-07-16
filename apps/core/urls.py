from django.urls import path
from . import views

urlpatterns = [
    path('api/reverse-geocode/', views.reverse_geocode, name='reverse_geocode'),
    path('api/search-location/', views.search_location, name='search_location'),
]
