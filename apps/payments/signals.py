from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment

@receiver(post_save, sender=Payment)
def update_order_status_on_payment(sender, instance, **kwargs):
    order = instance.order
    if instance.status == 'paid' and order.status != 'paid':
        order.status = 'paid'
        order.save()
    elif instance.status in ['expired', 'cancelled'] and order.status != instance.status:
        order.status = instance.status
        order.save()
