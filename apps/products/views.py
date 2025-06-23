from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from restaurants.models import Restaurant
from django.contrib.auth.decorators import login_required
from .forms import ProductForm, CategoryForm
from django.views.decorators.http import require_POST
from django.contrib import messages

@login_required
# List Produk
def product_list_view(request):
    # Pastikan user adalah merchant
    if not request.user.is_authenticated or request.user.role != 'merchant':
        return redirect('customer_login')

    restaurant = Restaurant.objects.filter(owner=request.user).first()

    if not restaurant:
        return redirect('restaurant_profile')

    # Handle tambah kategori jika request POST dari modal
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return redirect('product_list')  # Refresh page
    else:
        category_form = CategoryForm()

    products = Product.objects.filter(restaurant=restaurant)

    return render(request, 'merchant/products/product_list.html', {
        'products': products,
        'restaurant': restaurant,
        'category_form': category_form,  # ⬅️ ini penting
    })

@login_required
# Tambah Produk
def product_create_view(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.restaurant = restaurant
            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'merchant/products/product_form.html', {'form': form, 'title': 'Tambah Produk'})

@login_required
# Edit Produk
def product_update_view(request, pk):
    product = get_object_or_404(Product, pk=pk, restaurant__owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'merchant/products/product_form.html', {'form': form, 'title': 'Edit Produk'})

@login_required
# Hapus Produk
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk, restaurant__owner=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'merchant/products/product_confirm_delete.html', {'product': product})

@require_POST
@login_required
def category_create_view(request):
    if request.user.role != 'merchant':
        return redirect('customer_login')

    restaurant = Restaurant.objects.filter(owner=request.user).first()
    if not restaurant:
        return redirect('restaurant_profile')

    form = CategoryForm(request.POST)
    if form.is_valid():
        category = form.save(commit=False)
        category.restaurant = restaurant  # ⬅️ Ini bagian penting!
        category.save()
        messages.success(request, "Kategori berhasil ditambahkan.")
    else:
        messages.error(request, "Gagal menambahkan kategori.")

    return redirect('product_list')

