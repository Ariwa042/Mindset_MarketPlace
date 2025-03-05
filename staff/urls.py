from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Existing URLs
    path('', views.dashboard, name='dashboard'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Product image management
    path('products/image/<int:pk>/delete/', views.delete_product_image, name='delete_product_image'),
    
    # Order URLs
    path('orders/', views.order_list, name='order_list'),
    path('orders/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<uuid:order_id>/delete/', views.order_delete, name='order_delete'),
    
    # Contact Message URLs
    path('messages/', views.contact_messages, name='contact_messages'),
    path('messages/<int:pk>/', views.contact_message_detail, name='contact_message_detail'),
    
    # Analytics URLs
    path('analytics/', views.analytics, name='analytics'),
    
    # Subcategory URLs
    path('subcategories/', views.subcategory_list, name='subcategory_list'),
    path('subcategories/create/', views.subcategory_create, name='subcategory_create'),
    path('subcategories/<int:pk>/edit/', views.subcategory_edit, name='subcategory_edit'),
    path('subcategories/<int:pk>/delete/', views.subcategory_delete, name='subcategory_delete'),
    
    # User management URLs
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # Pi Transaction URLs
    path('pi-transactions/', views.pi_transaction_list, name='pi_transaction_list'),
    path('pi-transactions/<uuid:pk>/', views.pi_transaction_detail, name='pi_transaction_detail'),
    path('pi-wallets/', views.pi_wallet_list, name='pi_wallet_list'),
    path('pi-wallets/<int:pk>/', views.pi_wallet_detail, name='pi_wallet_detail'),
]
