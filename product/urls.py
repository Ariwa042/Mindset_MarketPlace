from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('search/', views.search_products, name='search_products'),
#    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('filter/', views.filter_products, name='filter_products'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
