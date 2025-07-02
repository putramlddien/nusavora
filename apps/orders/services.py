from .models import Order, OrderItem
from django.db import transaction

def create_order_from_cart(cart, payment_method):
    from payments.services import create_payment
    user = cart.user
    restaurant = cart.restaurant
    items = cart.items.all()
    total_price = sum([item.product.price * item.qty for item in items])

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            restaurant=restaurant,
            total_price=total_price,
            status='waiting_payment',
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