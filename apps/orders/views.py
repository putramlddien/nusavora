from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_GET, require_POST
from .models import Order

def is_merchant(user):
    # Ganti sesuai field merchant di user
    return hasattr(user, 'merchantprofile')

@login_required
@user_passes_test(is_merchant)
def update_order_process_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        next_status = request.POST.get('next_status')
        try:
            order.update_process_status(next_status, request.user)
            return JsonResponse({'success': True, 'new_status': order.process_status})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return HttpResponseForbidden()

@login_required
def customer_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return JsonResponse({
        'order_id': order.id,
        'status': order.status,
        'process_status': order.process_status,
        'delivery_type': order.delivery_type,
        'delivery_address': order.delivery_address,
        'created_at': order.created_at,
    })

@login_required
def customer_order_tracking(request):
    # Show the tracking page (with progress bar, polling, etc.)
    return render(request, 'customer/order_tracking.html')

@login_required
@require_POST
def customer_cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if not order.can_be_cancelled:
        return JsonResponse({'success': False, 'error': 'Pesanan tidak bisa dibatalkan.'}, status=400)
    order.status = 'cancelled'
    order.process_status = 'cancelled'
    order.save()
    return JsonResponse({'success': True})

# Create your views here.
