from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, SubCategory, Product

def product_list(request):
    products = Product.objects.filter(status='published')
    featured_products = products.filter(is_featured=True)[:4]
    categories = Category.objects.filter(is_active=True)
    
    # Filtering
    category_slug = request.GET.get('category')
    subcategory_slug = request.GET.get('subcategory')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', '-created_at')
    
    if category_slug:
        products = products.filter(subcategory__category__slug=category_slug)
    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    if sort:
        products = products.order_by(sort)
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'featured_products': featured_products,
        'categories': categories,
        'current_category': category_slug,
        'current_subcategory': subcategory_slug,
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
            Q(name__icontains=query) |
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
    
    products = Product.objects.filter(status='published')
    
    if category and category != 'all':
        if subcategory and subcategory != 'all':
            products = products.filter(subcategory__slug=subcategory)
        else:
            products = products.filter(subcategory__category__slug=category)
    
    context = {
        'products': products
    }
    
    return render(request, 'product/partials/product_list_partial.html', context)
