from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

# ─────────────────────────────────────────────────────────────
# Custom User Manager
# ─────────────────────────────────────────────────────────────

class NusavoraUserManager(BaseUserManager):
    def create_user(self, email, password=None, role='customer', **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(email, password, role='admin', is_staff=True, is_superuser=True, **extra_fields)

# ─────────────────────────────────────────────────────────────
# Custom User Model
# ─────────────────────────────────────────────────────────────

class NusavoraUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('merchant', 'Merchant'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)  # ➕ Tambahan baru
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'username']  # ➕ tambahkan username

    objects = NusavoraUserManager()

    def __str__(self):
        return f"{self.username} ({self.email}) - {self.role}"

# ─────────────────────────────────────────────────────────────
# OTP Model untuk Registrasi / Login
# ─────────────────────────────────────────────────────────────

class EmailOTP(models.Model):
    user = models.ForeignKey(NusavoraUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP for {self.user.email} | {self.otp_code}"
