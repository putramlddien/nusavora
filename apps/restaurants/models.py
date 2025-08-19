from django.db import models
from accounts.models import NusavoraUser
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from reviews.models import Review
from django.db.models import Avg

class Restaurant(models.Model):
    owner = models.ForeignKey(NusavoraUser, on_delete=models.CASCADE, limit_choices_to={'role': 'merchant'})
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='media/images/restaurant_logos/', blank=True, null=True)

    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    is_open = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Restaurant.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def avg_rating(self):
        from products.models import Product
        product_ct = ContentType.objects.get_for_model(Product)
        product_ids = self.products.values_list('id', flat=True)
        reviews = Review.objects.filter(content_type=product_ct, object_id__in=product_ids, is_approved=True)
        return round(reviews.aggregate(Avg('rating'))['rating__avg'] or 0, 1)

    @property
    def total_reviews(self):
        from products.models import Product
        product_ct = ContentType.objects.get_for_model(Product)
        product_ids = self.products.values_list('id', flat=True)
        return Review.objects.filter(content_type=product_ct, object_id__in=product_ids, is_approved=True).count()
    
    @property
    def product_categories(self):
        qs = self.products.filter(category__isnull=False).values_list('category__name', flat=True).distinct()
        return list(qs)

    def __str__(self):
        return self.name
