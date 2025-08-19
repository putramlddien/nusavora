from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from .forms import RegisterForm
from .models import NusavoraUser, EmailOTP
from django.core.mail import send_mail
import random
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm
from orders.models import Order
from django.contrib.auth.decorators import login_required, user_passes_test

def generate_otp():
    return str(random.randint(100000, 999999))

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            user.save()

            # Generate OTP
            otp_code = generate_otp()
            expires_at = timezone.now() + timedelta(minutes=10)
            EmailOTP.objects.create(user=user, otp_code=otp_code, expires_at=expires_at)


            # Kirim email OTP langsung (tanpa celery), tambahkan log sebelum dan sesudah
            print(f"[DEBUG] Akan mengirim OTP ke {user.email} dengan kode {otp_code}")
            try:
                result = send_mail(
                    subject="Kode OTP Anda untuk Nusavora",
                    message=f"Kode OTP kamu adalah {otp_code}. Jangan bagikan kode ini ke siapa pun.",
                    from_email="nusavoraid@gmail.com",
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                print(f"[DEBUG] Hasil send_mail: {result}")
            except Exception as e:
                print("ERROR SEND EMAIL:", e)
                from django.contrib import messages
                messages.error(request, f"Gagal mengirim email OTP: {e}")

            # Simpan email ke session untuk verifikasi
            request.session['otp_email'] = user.email
            return redirect('verify_otp')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def verify_otp_view(request):
    email = request.session.get('otp_email')

    if not email:
        return redirect('register')

    user = NusavoraUser.objects.filter(email=email).first()
    error = None

    if request.method == 'POST':
        otp_input = request.POST.get('otp')

        otp_obj = EmailOTP.objects.filter(user=user, otp_code=otp_input, is_verified=False).first()

        if otp_obj:
            if timezone.now() > otp_obj.expires_at:
                error = "Kode OTP sudah kadaluarsa."
            else:
                otp_obj.is_verified = True
                otp_obj.save()
                user.is_active = True
                user.save()
                # Bersihkan session OTP
                del request.session['otp_email']
                return redirect('customer_login')
        else:
            error = "Kode OTP tidak valid."

    return render(request, 'accounts/verify_otp.html', {'email': email, 'error': error})

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Redirect berdasarkan role
                    if user.role == 'merchant':
                        return redirect('/merchant/restaurant/dashboard/')
                    elif user.role == 'customer':
                        return redirect('/')
                    else:
                        return redirect('/')
                else:
                    messages.error(request, "Akun belum aktif. Silakan verifikasi OTP.")
            else:
                messages.error(request, "Email atau password salah.")
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    role = getattr(request.user, 'role', None)  # Cek role sebelum logout
    logout(request)

    if role == 'merchant':
        return redirect('customer_login')
    elif role == 'customer':
        return redirect('customer_login')
    else:
        return redirect('home')

def is_customer(user):
    return getattr(user, 'role', None) == 'customer'

@login_required
@user_passes_test(is_customer)
def customer_order_history(request):
    orders = (
        Order.objects
        .filter(user=request.user, process_status__in=['completed', 'cancelled', 'expired'])
        .order_by('-created_at')
        .select_related('restaurant')
        .prefetch_related('items__product')
    )
    return render(request, 'customer/order_history_drawer.html', {'order_history': orders})

