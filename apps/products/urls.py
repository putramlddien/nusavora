from django.urls import path
from .views import product_list_view, product_create_view, product_update_view, product_delete_view, category_create_view

urlpatterns = [
    path('', product_list_view, name='product_list'),
    path('tambah/', product_create_view, name='product_create'),
    path('<int:pk>/edit/', product_update_view, name='product_update'),
    path('<int:pk>/hapus/', product_delete_view, name='product_delete'),
    path('kategori/tambah/', category_create_view, name='category_create'),
]