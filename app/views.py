from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from geopy.distance import geodesic
from app.models import Vendor, Product
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


def get_nearby_vendors(user_lat, user_lon, radius=20):
    nearby_vendors = []
    for vendor in Vendor.objects.all():
        vendor_location = (vendor.latitude, vendor.longitude)
        user_location = (user_lat, user_lon)

        distance = geodesic(user_location, vendor_location).km
        if distance <= radius:  # Hanya ambil vendor dalam radius 5km
            nearby_vendors.append({"vendor": vendor, "distance": round(distance, 2)})

    return nearby_vendors

def get_vendors_by_location(request):
    user_lat = request.session.get("user_lat")
    user_lon = request.session.get("user_lon")

    if user_lat and user_lon:
        nearby_vendors = get_nearby_vendors(user_lat, user_lon)
        vendor_data = [
            {
                "name": vendor["vendor"].name,
                "category": ", ".join(set(Product.objects.filter(vendor=vendor["vendor"]).values_list("category", flat=True))),
                "distance": f"{vendor['distance']} km"
            }
            for vendor in nearby_vendors
        ]
        return JsonResponse({"vendors": vendor_data})

    return JsonResponse({"error": "Lokasi tidak ditemukan"})

def home(request):
    return render(request, "home.html")

def product(request):
    return render(request, "product.html")

def category(request):
    return render(request, "category.html")

def cart(request):
    return render(request, "cart.html")
    