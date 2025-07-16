import requests
from django.http import JsonResponse

def reverse_geocode(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lng')
    if not lat or not lon:
        return JsonResponse({'error': 'lat/lng required'}, status=400)
    try:
        res = requests.get(
            'https://nominatim.openstreetmap.org/reverse',
            params={'format': 'json', 'lat': lat, 'lon': lon, 'accept-language': 'id'},
            headers={'User-Agent': 'nusavora/1.0'}
        )
        data = res.json()
        address = data.get('display_name')
        if not address and 'address' in data:
            adr = data['address']
            address = adr.get('road') or adr.get('neighbourhood') or adr.get('village') or f"{lat}, {lon}"
        return JsonResponse({'display_name': address})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def search_location(request):
    query = request.GET.get('q')
    if not query:
        return JsonResponse({'error': 'q is required'}, status=400)
    try:
        res = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'format': 'json', 'q': query, 'countrycodes': 'id', 'accept-language': 'id'},
            headers={'User-Agent': 'nusavora/1.0'}
        )
        return JsonResponse(res.json(), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
