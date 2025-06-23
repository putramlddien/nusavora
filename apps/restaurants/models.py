from django.db import models
from accounts.models import NusavoraUser

class Restaurant(models.Model):
    owner = models.ForeignKey(NusavoraUser, on_delete=models.CASCADE, limit_choices_to={'role': 'merchant'})
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True)

    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    is_open = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
