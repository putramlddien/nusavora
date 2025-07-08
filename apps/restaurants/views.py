from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Restaurant
from .forms import RestaurantForm
from orders.models import Order
from django.views.decorators.http import require_POST
from django.http import JsonResponse

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

def is_merchant(user):
    return getattr(user, 'role', None) == 'merchant'  # atau user.is_merchant

@login_required
@user_passes_test(is_merchant)
def orders_active_view(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    orders = Order.get_active_orders_for_restaurant(restaurant)
    return render(request, 'merchant/orders_active.html', {'orders': orders})

@login_required
@user_passes_test(is_merchant)
def orders_incoming_view(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    orders = Order.objects.filter(restaurant=restaurant, process_status='waiting_confirmation')
    return render(request, 'merchant/orders_incoming.html', {'orders': orders})

@login_required
@user_passes_test(is_merchant)
@require_POST
def merchant_update_order_status(request, order_id):
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    order = get_object_or_404(Order, id=order_id, restaurant=restaurant)
    next_status = request.POST.get('next_status')
    try:
        order.update_process_status(next_status, request.user)
        # Auto-complete delivery: jika status diubah ke delivering, langsung set ke completed
        if next_status == 'delivering':
            order.update_process_status('completed', request.user)
        return JsonResponse({'success': True, 'new_status': order.process_status})
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)