from django.urls import path
from . import views

urlpatterns = [
    path('midtrans/webhook/', views.midtrans_webhook, name='midtrans_webhook'),
]
