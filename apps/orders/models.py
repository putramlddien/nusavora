from django.db import models
from django.conf import settings
from products.models import Product
from restaurants.models import Restaurant

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    order = models.OneToOneField('Order', null=True, blank=True, on_delete=models.SET_NULL, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Cart {self.id} - {self.restaurant.name}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.product.name} x {self.qty}"

class Order(models.Model):
    @property
    def can_be_cancelled(self):
        """
        Order hanya bisa dibatalkan jika belum completed/cancelled/expired.
        """
        return self.status not in ['cancelled', 'expired'] and not self.is_completed
    @property
    def is_active(self):
        """
        Order dianggap aktif jika status pembayaran belum selesai/cancel/expired.
        """
        return self.status in ['waiting_payment', 'pending']

    @property
    def is_completed(self):
        return self.process_status == 'completed'
    @staticmethod
    def get_active_order_for_user(user):
        """
        Return order with status waiting_payment for this user, if any.
        """
        return Order.objects.filter(user=user, status='waiting_payment').first()

    @staticmethod
    def get_active_orders_for_restaurant(restaurant):
        """
        Return queryset of active orders for a restaurant (not completed/cancelled/expired).
        """
        return Order.objects.filter(restaurant=restaurant).exclude(process_status__in=['completed', 'cancelled', 'expired'])
    def can_update_process_status(self, next_status):
        """
        Validasi transisi status proses order.
        - Payment harus paid sebelum proses jalan
        - Urutan status harus benar
        """
        if self.status != 'paid':
            return False, 'Pembayaran belum diterima.'
        valid_transitions = {
            'waiting_confirmation': ['processing'],
            'processing': ['ready_for_pickup', 'delivering'],
            'ready_for_pickup': ['completed'],
            'delivering': ['completed'],
        }
        if self.process_status not in valid_transitions:
            return False, 'Status tidak valid.'
        if next_status not in valid_transitions[self.process_status]:
            return False, f'Transisi dari {self.process_status} ke {next_status} tidak diizinkan.'
        return True, ''

    def update_process_status(self, next_status, user=None):
        can_update, msg = self.can_update_process_status(next_status)
        if not can_update:
            raise ValueError(msg)
        self.process_status = next_status
        self.save()
    # Status pembayaran (hanya untuk histori, status payment sebenarnya di Payment)
    STATUS_CHOICES = [
        ('pending', 'Pending'),                 # Order dibuat, belum bayar
        ('waiting_payment', 'Waiting Payment'), # Order sudah dibuat, menunggu pembayaran
        ('paid', 'Paid'),                       # Sudah dibayar
        ('expired', 'Expired'),                 # Pembayaran expired
        ('cancelled', 'Cancelled'),             # Order dibatalkan
    ]
    # Status proses order/pengiriman (utama untuk food delivery)
    PROCESS_STATUS_CHOICES = [
        ('waiting_confirmation', 'Menunggu Konfirmasi Resto'),
        ('processing', 'Diproses'),
        ('ready_for_pickup', 'Siap Diambil'),
        ('delivering', 'Dikirim'),
        ('completed', 'Selesai'),
    ]
    DELIVERY_TYPE_CHOICES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # pembayaran
    process_status = models.CharField(max_length=32, choices=PROCESS_STATUS_CHOICES, default='waiting_confirmation')
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPE_CHOICES, default='pickup')
    delivery_address = models.CharField(max_length=255, blank=True, null=True)
    delivery_note = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # snapshot info
    restaurant_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return f"Order {self.id} - {self.user} - {self.status}/{self.process_status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    qty = models.PositiveIntegerField(default=1)
    def __str__(self):
        return f"{self.product_name} x {self.qty}"
