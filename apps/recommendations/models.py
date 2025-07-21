from django.db import models
from accounts.models import NusavoraUser
from products.models import Product

class RecommendationCache(models.Model):
    user = models.ForeignKey(NusavoraUser, on_delete=models.CASCADE, related_name='cached_recommendations')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-score']
