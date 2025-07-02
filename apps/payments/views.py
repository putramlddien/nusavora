from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .services import handle_midtrans_webhook
import json

@csrf_exempt
def midtrans_webhook(request):
    data = json.loads(request.body)
    handle_midtrans_webhook(data)
    return JsonResponse({'status': 'ok'})
