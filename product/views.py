from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, SubCategory, Product
import random
from django.db.models import Prefetch


def product_list(request):
    categories = Category.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            'subcategories',
            queryset=SubCategory.objects.filter(is_active=True)
        )
    )

    context = {
        'featured_products': Product.objects.filter(
            is_featured=True, 
            status='published'
        )[:8],
        'top_categories': categories,  # Now includes subcategories
        'best_sellers': Product.objects.filter(
            status='published'
        ).order_by('-sales')[:4],
    }
    return render(request, 'product/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, status='published')
    related_products = Product.objects.filter(
        subcategory=product.subcategory,
        status='published'
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product/product_detail.html', context)

def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    subcategories = category.subcategories.filter(is_active=True)
    products = Product.objects.filter(
        subcategory__category=category,
        status='published'
    )
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'page_obj': page_obj,
    }
    return render(request, 'product/category_detail.html', context)

def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(status='published')
    
    if query:
        products = products.filter(
            Q(name__icontains(query)) |
            Q(description__icontains(query)) |
            Q(meta_keywords__icontains(query)) |
            Q(subcategory__name__icontains(query)) |
            Q(subcategory__category__name__icontains(query))
        ).distinct()
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'page_obj': page_obj,
    }
    return render(request, 'product/search_results.html', context)

def filter_products(request):
    category = request.GET.get('category')
    subcategory = request.GET.get('subcategory')
    
    # Start with all published products
    products = Product.objects.filter(status='published')
    
    # Apply category filter
    if category and category != 'all':
        if subcategory and subcategory != 'all':
            products = products.filter(subcategory__slug=subcategory)
        else:
            products = products.filter(subcategory__category__slug=category)
    
    # Handle sorting
    if category == 'all':
        # Convert queryset to list for random shuffling
        products = list(products)
        random.shuffle(products)
    else:
        # Default sorting by newest first
        products = products.order_by('-created_at')
    
    context = {
        'products': products,
        'current_category': category,
        'current_subcategory': subcategory
    }
    
    return render(request, 'product/partials/product_list_partial.html', context)
