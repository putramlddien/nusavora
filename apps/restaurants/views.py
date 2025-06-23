from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Restaurant
from .forms import RestaurantForm

@login_required
def dashboard_view(request):
    # Dummy data analitik
    sales_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun']
    sales_data = [250000, 320000, 290000, 400000, 370000, 500000]

    product_labels = ['Nasi Goreng', 'Ayam Bakar', 'Es Teh', 'Burger']
    product_data = [120, 90, 150, 100]

    context = {
        'sales_labels': sales_labels,
        'sales_data': sales_data,
        'product_labels': product_labels,
        'product_data': product_data,
        'total_sales': 2130000,
        'product_count': 25,
        'restaurant_count': 2,
    }
    return render(request, 'merchant/dashboard.html', context)

@login_required
def restaurant_profile_view(request):
    user = request.user

    # Ambil atau buat restoran milik merchant
    restaurant, created = Restaurant.objects.get_or_create(owner=user)

    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            return redirect('restaurant_profile')
    else:
        form = RestaurantForm(instance=restaurant)

    return render(request, 'merchant/restaurant_profile.html', {
        'form': form,
        'restaurant': restaurant,
        'created': created
    })