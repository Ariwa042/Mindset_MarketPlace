from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('connect-wallet/', views.connect_wallet, name='connect_wallet'),
    path('process/<uuid:order_id>/', views.process_payment, name='process_payment'),
]
