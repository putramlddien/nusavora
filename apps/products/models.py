from accounts.models import NusavoraUser
from django.db import models
from restaurants.models import Restaurant
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    is_global = models.BooleanField(default=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='media/images/category_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    is_available = models.BooleanField(default=True)
    is_customizable = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"
