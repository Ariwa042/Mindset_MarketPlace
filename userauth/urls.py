from django.urls import path
from . import views

app_name = 'userauth'

urlpatterns = [
    # Authentication URLs
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    
    # Email Verification URLs
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('check-email/', views.check_email, name='check_email'),
    
    # Profile Management URLs
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Password Reset URLs
    path('forgot-password/', views.forgotten_password, name='forgotten_password'),
    path('verify-reset-otp/', views.verify_reset_otp, name='verify_reset_otp'),
]
