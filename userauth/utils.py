from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import random
from datetime import timedelta
from .models import OTP

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_otp_email(user):
    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=10)
    
    # Save OTP to database
    OTP.objects.create(
        user=user,
        otp=otp_code,
        expires_at=expires_at
    )
    
    # Send email
    subject = 'Your OTP for Email Verification'
    message = f'Your OTP is: {otp_code}. This code will expire in 10 minutes.'
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
