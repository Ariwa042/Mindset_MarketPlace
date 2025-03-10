from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random

def send_otp_email(email, otp):
    subject = 'Your Pi Marketplace Verification Code'
    html_message = render_to_string('userauth/emails/otp_email.html', {
        'otp': otp
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"OTP email sent successfully to {email}")  # Debugging
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {str(e)}")  # Debugging
        return False

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])
