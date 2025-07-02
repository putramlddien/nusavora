from accounts.models import NusavoraUser
from django.db import models
from restaurants.models import Restaurant
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from reviews.models import Review

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
    image = models.ImageField(upload_to='media/images/product_images/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    is_available = models.BooleanField(default=True)
    is_customizable = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"
    
    @property
    def avg_rating(self):
        ct = ContentType.objects.get_for_model(self.__class__)
        reviews = Review.objects.filter(content_type=ct, object_id=self.id, is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return None

    @property
    def total_reviews(self):
        ct = ContentType.objects.get_for_model(self.__class__)
        return Review.objects.filter(content_type=ct, object_id=self.id, is_approved=True).count()
