from .models import Order, OrderItem
from django.db import transaction

def create_order_from_cart(cart, payment_method, delivery_type, delivery_address=None, delivery_note=None):
    """
    Buat order dari cart, dengan validasi delivery_type dan address.
    """
    from payments.services import create_payment
    user = cart.user
    restaurant = cart.restaurant
    items = cart.items.all()
    total_price = sum([item.product.price * item.qty for item in items])

    if delivery_type == 'delivery' and not delivery_address:
        raise ValueError('Alamat pengantaran wajib diisi untuk delivery.')

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            restaurant=restaurant,
            total_price=total_price,
            status='waiting_payment',
            process_status='waiting_confirmation',
            delivery_type=delivery_type,
            delivery_address=delivery_address if delivery_type == 'delivery' else '',
            delivery_note=delivery_note or '',
            restaurant_name=restaurant.name,
            address=restaurant.address,
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                qty=item.qty,
            )
        payment, payment_details = create_payment(order, payment_method)
        cart.order = order
        cart.save()
    return order, payment, payment_details