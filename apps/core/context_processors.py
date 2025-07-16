from django.conf import settings

def global_settings(request):
    return {
        'RECOMMENDATION_API_BASE': getattr(settings, 'RECOMMENDATION_API_BASE', 'http://localhost:8000'),
    }