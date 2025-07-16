from django.db import models
from accounts.models import NusavoraUser
from products.models import Product
from orders.models import Cart, Order

class ProductViewLog(models.Model):
    user = models.ForeignKey(NusavoraUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

class AddToCartLog(models.Model):
    user = models.ForeignKey(NusavoraUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

class PurchaseLog(models.Model):
    user = models.ForeignKey(NusavoraUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)