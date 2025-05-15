from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from geopy.distance import geodesic
from app.models import Vendor, Product, Category
import json

@csrf_exempt
def set_location(request):
    if request.method == "POST":
        data = json.loads(request.body)
        request.session["user_lat"] = data["latitude"]
        request.session["user_lon"] = data["longitude"]
        return JsonResponse({"status": "success"})
    return JsonResponse({"error": "Invalid request"}, status=400)

def get_location(request):
    user_lat = request.session.get("user_lat", "Tidak Diketahui")
    user_lon = request.session.get("user_lon", "Tidak Diketahui")
    
    if user_lat and user_lon:
        return JsonResponse({"latitude": user_lat, "longitude": user_lon})

    return JsonResponse({"error": "Lokasi tidak ditemukan"})

def get_nearby_vendors(user_lat, user_lon, radius=15):
    nearby_vendors = []
    for vendor in Vendor.objects.all():
        vendor_location = (vendor.latitude, vendor.longitude)
        user_location = (user_lat, user_lon)

        distance = geodesic(user_location, vendor_location).km
        if distance <= radius:  # Hanya ambil vendor dalam radius 15km
            nearby_vendors.append({"vendor": vendor, "distance": round(distance, 2)})

    return nearby_vendors

def get_vendors_by_location(request):
    user_lat = request.session.get("user_lat")
    user_lon = request.session.get("user_lon")

    if user_lat and user_lon:
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
        except Exception:
            return JsonResponse({"vendors": []})
        nearby_vendors = get_nearby_vendors(user_lat, user_lon)
        vendor_data = [
            {
                "name": vendor["vendor"].name,
                "category": vendor["vendor"].category.name if hasattr(vendor["vendor"], "category") and vendor["vendor"].category else "-",
                "distance": f"{vendor['distance']} km"
            }
            for vendor in nearby_vendors
        ]
        return JsonResponse({"vendors": vendor_data})

    return JsonResponse({"vendors": []})

def home(request):
    categories = Category.objects.all()
    vendor = Vendor.objects.all()
    return render(request, "home.html", {"categories": categories, "vendor": vendor})

def vendor_page(request, location=None):
    user_lat = request.GET.get("lat")
    user_lon = request.GET.get("lon")

    if user_lat and user_lon:
        user_location = (float(user_lat), float(user_lon))
        vendors = []
        for vendor in Vendor.objects.all():
            vendor_location = (vendor.latitude, vendor.longitude)
            distance = geodesic(user_location, vendor_location).km
            if distance <= 20:
                # Ambil kategori produk unik yang dijual vendor
                categories = Product.objects.filter(vendor=vendor, category__isnull=False).values_list('category__name', flat=True).distinct()
                vendors.append({
                    "vendor": vendor,
                    "categories": ", ".join(categories) if categories else "-",
                    "distance": round(distance, 2)
                })
        return render(request, "vendor.html", {"location": f"{user_lat}, {user_lon}", "vendors": vendors})

    return render(request, "vendor.html", {"location": "Lokasi tidak diketahui", "vendors": []})

def product(request):
    return render(request, "product.html")

def category(request):
    return render(request, "category.html")

def cart(request):
    return render(request, "cart.html")
