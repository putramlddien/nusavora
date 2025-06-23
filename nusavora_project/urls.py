from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.customer.views import customer_landing_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # URL accounts: login, register, OTP
    path('accounts/', include('accounts.urls')), 
    path('merchant/restaurant/', include('restaurants.urls')),
    path('merchant/products/', include('products.urls')),
    path('', customer_landing_view, name='home'),
    path('customer/', include('customer.urls')),

]

# Serve media/static in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
