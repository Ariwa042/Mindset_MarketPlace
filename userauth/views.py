from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, SignInForm, ProfileUpdateForm
from datetime import datetime, timedelta
from .models import CustomUser  # Add CustomUser import
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import JsonResponse
from django.conf import settings


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('core:home')
    else:
        form = SignUpForm()
    return render(request, 'userauth/signup.html', {'form': form})

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
    """Handle forgotten password"""
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
            # Store user_id in session for password change
            request.session['reset_user_id'] = user.id
            return redirect('userauth:change_password')
            
        except ObjectDoesNotExist:
            messages.error(request, 'No user found with this email address.')
            
    return render(request, 'userauth/forgot_password.html')

# Remove verify_reset_otp function as it's no longer needed

def check_email(request):
    """AJAX endpoint to check if email exists"""
    email = request.GET.get('email', '')
    exists = CustomUser.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})