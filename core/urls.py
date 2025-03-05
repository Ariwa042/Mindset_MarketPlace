from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.contact, name='contact'),
]
