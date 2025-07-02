import requests
from .models import Payment
from django.conf import settings
import base64

MIDTRANS_SERVER_KEY = settings.MIDTRANS_SERVER_KEY
encoded_key = base64.b64encode(MIDTRANS_SERVER_KEY.encode()).decode()
MIDTRANS_BASE_URL = 'https://api.sandbox.midtrans.com/v2/charge'

def create_payment(order, payment_method):
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Basic {encoded_key}',
    }

    payload = {
        "transaction_details": {
            "order_id": f"ORDER-{order.id}",
            "gross_amount": int(order.total_price),
        },
        "customer_details": {
            "first_name": order.user.full_name,
            "email": order.user.email,
        }
    }

    if payment_method.endswith('_va'):
        bank = payment_method.replace('_va', '')
        payload["payment_type"] = 'bank_transfer'
        payload["bank_transfer"] = {"bank": bank}

    elif payment_method == 'qris':
        payload["payment_type"] = 'qris'

    elif payment_method == 'gopay':
        payload["payment_type"] = 'gopay'

    elif payment_method == 'indomaret':
        payload["payment_type"] = 'cstore'
        payload["cstore"] = {
            "store": "indomaret",  # kecil semua!
            "message": "Pembayaran di Indomaret"
        }

    elif payment_method == 'alfamart':
        payload["payment_type"] = 'cstore'
        payload["cstore"] = {
            "store": "alfamart",  # kecil semua!
            "message": "Pembayaran di Alfamart"
        }

    else:
        raise Exception('Metode pembayaran tidak didukung')

    response = requests.post(MIDTRANS_BASE_URL, json=payload, headers=headers)
    data = response.json()

    # log data untuk debugging
    print("== Midtrans Response ==")
    print("Payload:", payload)
    print("Full Data:", data)

    va_number = ''
    qr_url = ''
    redirect_url = ''
    if 'redirect_url' in data:
        redirect_url = data['redirect_url']
    elif 'actions' in data:
        for action in data['actions']:
            if action.get('name') in ['deeplink-redirect', 'payment-url']:
                redirect_url = action.get('url')
                break

    if 'va_numbers' in data and data['va_numbers']:
        va_number = data['va_numbers'][0]['va_number']

    if 'actions' in data:
        for action in data['actions']:
            if action.get('name') == 'generate-qr-code':
                qr_url = action.get('url')

    # Tambahan: untuk indomaret/alfamart kadang URL redirect di data['actions']
    if not redirect_url and 'actions' in data:
        for action in data['actions']:
            if action.get('name') == 'deeplink-redirect':
                redirect_url = action.get('url')

    payment_code = data.get('payment_code', '')

    payment = Payment.objects.create(
        order=order,
        payment_ref=payload["transaction_details"]["order_id"],
        method=payment_method,
        status='waiting',
        amount=order.total_price,
        va_number=va_number,
        qr_url=qr_url,
        redirect_url=redirect_url,
        payment_code=payment_code,
    )

    return payment, {
        'va_number': va_number,
        'qr_url': qr_url,
        'redirect_url': redirect_url,
    }

def update_payment_status(payment_ref, status):
    payment = Payment.objects.get(payment_ref=payment_ref)
    payment.status = status
    payment.save()
    order = payment.order
    if status == 'paid':
        order.status = 'paid'
        # Hapus cart setelah payment sukses, JANGAN hapus order/payment!
        if hasattr(order, 'cart'):
            order.cart.delete()
    elif status == 'expired':
        order.status = 'expired'
        # Hapus cart setelah payment expired, JANGAN hapus order/payment!
        if hasattr(order, 'cart'):
            order.cart.delete()
    order.save()
    return payment

def handle_midtrans_webhook(data):
    order_id = data.get('order_id')
    transaction_status = data.get('transaction_status')
    if transaction_status == 'settlement':
        update_payment_status(order_id, 'paid')
    elif transaction_status in ['expire', 'cancel']:
        update_payment_status(order_id, 'expired')

def fetch_and_update_payment_details(payment):
    order_id = payment.payment_ref
    url = f'https://api.sandbox.midtrans.com/v2/{order_id}/status'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Basic {encoded_key}',
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    # Update VA number jika ada
    va_number = ''
    if 'va_numbers' in data and data['va_numbers']:
        va_number = data['va_numbers'][0].get('va_number', '')
    # Update QRIS jika ada
    qr_url = ''
    if 'actions' in data and data['actions']:
        for action in data['actions']:
            if action.get('name') == 'generate-qr-code':
                qr_url = action.get('url', '')
    payment.va_number = va_number
    payment.qr_url = qr_url
    payment.save()
    return payment
