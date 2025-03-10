from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, SignInForm, OTPVerificationForm, ProfileUpdateForm
from datetime import datetime, timedelta
from .utils import send_otp_email
from .models import OTP, CustomUser  # Add CustomUser import
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import JsonResponse
import random  # Add this for OTP generation


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Store form data in session
            request.session['signup_data'] = {
                'email': email,
                'password1': form.cleaned_data['password1'],
                'password2': form.cleaned_data['password2']
            }
            
            try:
                send_otp_email(email)
                messages.success(request, 'OTP sent to your email.')
                return redirect('userauth:verify_otp')
            except Exception as e:
                messages.error(request, 'Error sending OTP. Please try again.')
                return redirect('userauth:signup')
    else:
        form = SignUpForm()
    return render(request, 'userauth/signup.html', {'form': form})

def verify_otp(request):
    signup_data = request.session.get('signup_data')
    if not signup_data:
        messages.error(request, 'Please complete signup form first.')
        return redirect('userauth:signup')
        
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            email = signup_data['email']
            
            try:
                # Verify OTP
                otp_obj = OTP.objects.filter(
                    email=email,
                    otp=otp,
                    expires_at__gt=timezone.now()
                ).latest('created_at')
                
                # Create user account - username will be automatically generated
                user = CustomUser.objects.create_user(
                    email=signup_data['email'],
                    password=signup_data['password1']
                )
                user.is_active = True
                user.save()
                
                # Delete used OTP and session data
                otp_obj.delete()
                del request.session['signup_data']
                
                # Log user in
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('core:home')
                
            except OTP.DoesNotExist:
                messages.error(request, 'Invalid or expired OTP.')
    else:
        form = OTPVerificationForm()
        
    return render(request, 'userauth/verify_otp.html', {'form': form})

def resend_otp(request):
    signup_data = request.session.get('signup_data')
    if not signup_data:
        messages.error(request, 'Please complete signup form first.')
        return redirect('userauth:signup')
        
    try:
        send_otp_email(signup_data['email'])
        messages.success(request, 'New OTP has been sent to your email.')
    except Exception as e:
        messages.error(request, 'Error sending OTP. Please try again.')
    
    return redirect('userauth:verify_otp')

def send_otp_email(email):
    """Generate and send OTP"""
    from .utils import generate_otp, send_otp_email as send_email
    
    otp = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=10)
    
    try:
        # Delete any existing OTPs for this email
        OTP.objects.filter(email=email).delete()
        
        # Create new OTP record
        otp_obj = OTP.objects.create(
            email=email,
            otp=otp,
            expires_at=expires_at
        )
        
        # Send email
        if send_email(email, otp):
            return True
        else:
            otp_obj.delete()
            raise Exception("Failed to send OTP email")
            
    except Exception as e:
        print(f"Error in send_otp_email: {str(e)}")  # Debugging
        raise

def signin(request):
    if request.method == 'POST':
        form = SignInForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Set session expiry to 2 weeks if remember_me is checked
            if form.cleaned_data.get('remember_me'):
                request.session.set_expiry(1209600)  # 2 weeks in seconds
            else:
                request.session.set_expiry(0)  # Browser close
                
            messages.success(request, 'Login successful.')
            return redirect('core:home')
        messages.error(request, 'Invalid username or password.')
    else:
        form = SignInForm()
    return render(request, 'userauth/signin.html', {'form': form})

@login_required
def signout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('core:home')

def password_reset(request):
    pass

@login_required
def profile_view(request):
    """View user profile information"""
    orders = request.user.orders.all()[:5]  # Get last 5 orders
    context = {
        'user': request.user,
        'profile': request.user.profile,
        'recent_orders': orders
    }
    return render(request, 'userauth/profile/view.html', context)

@login_required
def profile_edit(request):
    """Edit profile information"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('userauth:profile_view')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'userauth/profile/edit.html', {'form': form})

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(old_password):
            messages.error(request, 'Your old password was entered incorrectly.')
        elif new_password1 != new_password2:
            messages.error(request, 'The two password fields didn’t match.')
        else:
            request.user.set_password(new_password1)
            request.user.save()
            login(request, request.user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('userauth:profile_view')

    return render(request, 'userauth/profile/change_password.html')

def forgotten_password(request):
    """Handle forgotten password with OTP verification"""
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
            
            # Send OTP
            send_otp_email(user)
            
            # Store user_id in session for verification
            request.session['reset_user_id'] = user.id
            messages.success(request, 'An OTP has been sent to your email.')
            return redirect('userauth:verify_reset_otp')
            
        except ObjectDoesNotExist:
            messages.error(request, 'No user found with this email address.')
            
    return render(request, 'userauth/forgot_password.html')


def verify_reset_otp(request):
    """Verify OTP for password reset"""
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Please start the password reset process again.')
        return redirect('userauth:forgotten_password')
        
    if request.method == 'POST':
        otp = request.POST.get('otp')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        try:
            otp_obj = OTP.objects.filter(
                user_id=user_id,
                otp=otp,
                expires_at__gt=timezone.now()
            ).latest('created_at')
            
            if new_password1 != new_password2:
                messages.error(request, 'The two password fields didn’t match.')
            else:
                user = otp_obj.user
                user.set_password(new_password1)
                user.save()
                
                # Delete used OTP
                otp_obj.delete()
                
                # Clear session
                del request.session['reset_user_id']
                
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('userauth:signin')
                
        except OTP.DoesNotExist:
            messages.error(request, 'Invalid or expired OTP.')
            
    return render(request, 'userauth/verify_reset_otp.html')

def check_email(request):
    """AJAX endpoint to check if email exists"""
    email = request.GET.get('email', '')
    exists = CustomUser.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})