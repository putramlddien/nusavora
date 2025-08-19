from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.customer.views import landing_page_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('merchant/restaurant/', include('restaurants.urls')),
    path('merchant/products/', include('products.urls')),
    path('payments/', include('payments.urls')),
    path('', include('customer.urls')),
    path('recommendations/', include('recommendations.urls')),
    path('core/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)