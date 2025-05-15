from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from app.views import home, set_location, get_location, category, cart, product, get_vendors_by_location, vendor_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path('set-location/', set_location, name="set_location"),
    path('get-location/', get_location, name="get_location"),
    path("get-vendors/", get_vendors_by_location, name="get_vendors"),
    path("vendor/", vendor_page, name="vendor_page"),
    path('<str:location>/', vendor_page, name="vendor_page_old"),
    path('category/', category, name="category"),
    path('product/', product, name="product"),
    path('cart/', cart, name="cart"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
