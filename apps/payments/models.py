from django.db import models
from orders.models import Order

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('waiting', 'Waiting Payment'),
        ('paid', 'Paid'),
        ('expired', 'Expired'),
        ('failed', 'Failed'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_ref = models.CharField(max_length=100, unique=True)
    method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    snap_token = models.CharField(max_length=255, blank=True, null=True)
    va_number = models.CharField(max_length=100, blank=True, null=True)
    qr_url = models.URLField(blank=True, null=True)
    redirect_url = models.URLField(blank=True, null=True)
    payment_code = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Payment {self.payment_ref} - {self.status}"
