from django.urls import path
from . import views

app_name = 'userauth'

urlpatterns = [
    # Authentication URLs
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Password Reset URLs
    path('forgot-password/', views.forgotten_password, name='forgotten_password'),
]
