from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from .models import StaffMember, ActivityLog, SiteAnalytics
from django.core.paginator import Paginator
from .decorators import staff_required
from product.models import Product, Category, SubCategory, ProductImages
from order.models import Order, Cart
from userauth.models import CustomUser
import csv
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from core.models import ContactMessage
from .forms import (
    CategoryForm, SubCategoryForm, ProductForm, 
    OrderStatusUpdateForm, ContactMessageResponseForm,
    UserCreateForm, UserEditForm, UserProfileForm
)
from django.core.mail import send_mail
from django.conf import settings
from payment.models import PiWallet, PiTransaction

@login_required
@staff_required
def dashboard(request):
    """Staff dashboard with key metrics and recent activity"""
    today = timezone.now().date()
    
    context = {
        'daily_sales': Order.objects.filter(created_at__date=today).aggregate(
            total=Sum('total_amount'))['total'] or 0,
        'pending_orders': Order.objects.filter(status='pending').count(),
        'low_stock_products': Product.objects.filter(stock__lte=10).count(),
        'recent_orders': Order.objects.all()[:5],
        'recent_activities': ActivityLog.objects.all()[:10],
        'total_customers': CustomUser.objects.count(),
    }
    return render(request, 'staff/dashboard.html', context)

@login_required
@staff_required
def product_management(request):
    """Product management view"""
    products = Product.objects.all().select_related('subcategory')
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    return render(request, 'staff/products/list.html', {'products': products})

@login_required
@staff_required
def analytics(request):
    """Analytics and reporting view"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    analytics_data = {
        'sales_by_day': Order.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).values('created_at__date').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ),
        'top_products': Product.objects.annotate(
            total_sales=Count('orderitem')
        ).order_by('-total_sales')[:10],
        'customer_growth': CustomUser.objects.filter(
            date_joined__date__range=[start_date, end_date]
        ).values('date_joined__date').annotate(
            count=Count('id')
        )
    }
    return render(request, 'staff/analytics.html', analytics_data)

@login_required
@staff_required
def export_data(request, data_type):
    """Export data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{data_type}_{datetime.now()}.csv"'
    
    writer = csv.writer(response)
    
    if data_type == 'orders':
        writer.writerow(['Order ID', 'Customer', 'Amount', 'Status', 'Date'])
        orders = Order.objects.all()
        for order in orders:
            writer.writerow([
                order.id,
                order.user.email,
                order.total_amount,
                order.status,
                order.created_at
            ])
    
    return response

@login_required
@staff_required
def user_management(request):
    """User management view"""
    users = CustomUser.objects.all()
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    return render(request, 'staff/users/list.html', {'users': users})

@login_required
@staff_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'staff/category/list.html', {'categories': categories})

@login_required
@staff_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('staff:category_list')
    else:
        form = CategoryForm()
    return render(request, 'staff/category/form.html', {'form': form})

@login_required
@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('staff:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'staff/category/form.html', {'form': form, 'category': category})

@login_required
@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('staff:category_list')
    return render(request, 'staff/category/delete.html', {'category': category})

@login_required
@staff_required
def product_list(request):
    products = Product.objects.select_related('subcategory__category')
    return render(request, 'staff/product/list.html', {'products': products})

@login_required
@staff_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            
            # Handle additional images
            for image in request.FILES.getlist('additional_images'):
                ProductImages.objects.create(product=product, images=image)
            
            messages.success(request, 'Product created successfully.')
            return redirect('staff:product_list')
    else:
        form = ProductForm()
    return render(request, 'staff/product/form.html', {'form': form})

@login_required
@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            
            # Handle additional images
            for image in request.FILES.getlist('additional_images'):
                ProductImages.objects.create(product=product, images=image)
            
            messages.success(request, 'Product updated successfully.')
            return redirect('staff:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'staff/product/form.html', {'form': form, 'product': product})

@login_required
@staff_required
def order_list(request):
    orders = Order.objects.select_related('user').prefetch_related('items')
    return render(request, 'staff/order/list.html', {'orders': orders})

@login_required
@staff_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            order.update_status(
                order.status,
                user=request.user,
                notes=request.POST.get('notes', '')
            )
            messages.success(request, 'Order status updated successfully.')
            
            # Log activity
            ActivityLog.objects.create(
                staff=request.user.staffmember,
                action='update',
                content_type='order',
                object_id=order_id,
                description=f'Updated order status: {order.id} to {order.status}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return redirect('staff:order_list')
    else:
        form = OrderStatusUpdateForm(instance=order)
    return render(request, 'staff/order/detail.html', {
        'order': order,
        'form': form,
        'status_history': order.status_history.all()
    })

@login_required
@staff_required
def contact_messages(request):
    messages = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'staff/contact/list.html', {'messages': messages})

@login_required
@staff_required
def contact_message_detail(request, pk):
    contact_message = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        form = ContactMessageResponseForm(request.POST)
        if form.is_valid():
            # Send response email
            response = form.cleaned_data['response']
            send_mail(
                subject=f'Re: {contact_message.subject}',
                message=response,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contact_message.email],
            )
            contact_message.is_resolved = True
            contact_message.save()
            messages.success(request, 'Response sent successfully.')
            return redirect('staff:contact_messages')
    else:
        form = ContactMessageResponseForm()
    return render(request, 'staff/contact/detail.html', {
        'message': contact_message,
        'form': form
    })

@login_required
@staff_required
def subcategory_list(request):
    category_id = request.GET.get('category')
    subcategories = SubCategory.objects.select_related('category')
    
    if category_id:
        subcategories = subcategories.filter(category_id=category_id)
    
    categories = Category.objects.all()
    
    context = {
        'subcategories': subcategories,
        'categories': categories,
        'selected_category': category_id
    }
    return render(request, 'staff/subcategory/list.html', context)

@login_required
@staff_required
def user_list(request):
    query = request.GET.get('q')
    role = request.GET.get('role')
    
    users = CustomUser.objects.all()
    
    if query:
        users = users.filter(
            Q(email__icontains(query)) |
            Q(first_name__icontains(query)) |
            Q(last_name__icontains(query))
        )
    
    if role:
        if role == 'admin':
            users = users.filter(is_superuser=True)
        elif role == 'staff':
            users = users.filter(staffmember__isnull=False)
        elif role == 'customer':
            users = users.filter(staffmember__isnull=True, is_superuser=False)
    
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    return render(request, 'staff/users/list.html', {'users': users})

@login_required
@staff_required
def user_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    orders = user.orders.all()[:5]
    
    context = {
        'user_detail': user,
        'recent_orders': orders,
        'profile': user.profile
    }
    return render(request, 'staff/users/detail.html', context)

@login_required
@staff_required
def toggle_user_status(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=pk)
        if not user.is_superuser:
            user.is_active = not user.is_active
            user.save()
            
            # Log activity
            ActivityLog.objects.create(
                staff=request.user.staffmember,
                action='update',
                content_type='user',
                object_id=pk,
                description=f'Toggle user status: {user.email} to {user.is_active}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
@staff_required
def user_create(request):
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            messages.success(request, 'User created successfully.')
            return redirect('staff:user_list')
    else:
        user_form = UserCreateForm()
        profile_form = UserProfileForm()
    
    return render(request, 'staff/users/form.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
@staff_required
def user_edit(request, pk):
    user_obj = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user_obj)
        profile_form = UserProfileForm(request.POST, instance=user_obj.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('staff:user_list')
    else:
        user_form = UserEditForm(instance=user_obj)
        profile_form = UserProfileForm(instance=user_obj.profile)
    
    return render(request, 'staff/users/form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_obj': user_obj
    })

@login_required
@staff_required
def subcategory_create(request):
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcategory created successfully.')
            return redirect('staff:subcategory_list')
    else:
        form = SubCategoryForm()
    
    return render(request, 'staff/subcategory/form.html', {'form': form})

@login_required
@staff_required
def subcategory_edit(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, request.FILES, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcategory updated successfully.')
            return redirect('staff:subcategory_list')
    else:
        form = SubCategoryForm(instance=subcategory)
    
    return render(request, 'staff/subcategory/form.html', {
        'form': form,
        'subcategory': subcategory
    })

@login_required
@staff_required
def subcategory_delete(request, pk):
    """Delete subcategory after confirmation"""
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        category_id = subcategory.category.id
        subcategory.delete()
        messages.success(request, 'Subcategory deleted successfully.')
        
        # Log activity
        ActivityLog.objects.create(
            staff=request.user.staffmember,
            action='delete',
            content_type='subcategory',
            object_id=pk,
            description=f'Deleted subcategory: {subcategory.name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return redirect('staff:category_detail', pk=category_id)
    return render(request, 'staff/subcategory/delete.html', {'subcategory': subcategory})

@login_required
@staff_required
def order_delete(request, order_id):
    """Delete order after confirmation"""
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully.')
        
        # Log activity
        ActivityLog.objects.create(
            staff=request.user.staffmember,
            action='delete',
            content_type='order',
            object_id=order_id,
            description=f'Deleted order: {order_id}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return redirect('staff:order_list')
    return render(request, 'staff/order/delete.html', {'order': order})

@login_required
@staff_required
def user_delete(request, pk):
    """Delete user after confirmation"""
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        if user.is_superuser:
            messages.error(request, 'Cannot delete superuser accounts.')
            return redirect('staff:user_list')
            
        user.delete()
        messages.success(request, 'User deleted successfully.')
        
        # Log activity
        ActivityLog.objects.create(
            staff=request.user.staffmember,
            action='delete',
            content_type='user',
            object_id=pk,
            description=f'Deleted user: {user.email}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return redirect('staff:user_list')
    return render(request, 'staff/users/delete.html', {'user_obj': user})

@login_required
@staff_required
def product_delete(request, pk):
    """Delete product after confirmation"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        
        # Log activity
        ActivityLog.objects.create(
            staff=request.user.staffmember,
            action='delete',
            content_type='product',
            object_id=pk,
            description=f'Deleted product: {product.name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return redirect('staff:product_list')
    return render(request, 'staff/product/delete.html', {'product': product})

@login_required
@staff_required
def pi_transaction_list(request):
    """List all Pi transactions"""
    transactions = PiTransaction.objects.select_related('wallet', 'order').all()
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)
    
    paginator = Paginator(transactions, 20)
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    
    context = {
        'transactions': transactions,
        'status_choices': PiTransaction.STATUS_CHOICES
    }
    return render(request, 'staff/payment/transaction_list.html', context)

@login_required
@staff_required
def pi_transaction_detail(request, pk):
    """View Pi transaction details"""
    transaction = get_object_or_404(PiTransaction, pk=pk)
    return render(request, 'staff/payment/transaction_detail.html', {
        'transaction': transaction
    })

@login_required
@staff_required
def pi_wallet_list(request):
    """List all Pi wallets"""
    wallets = PiWallet.objects.select_related('user').all()
    
    # Filter by verification status
    is_verified = request.GET.get('verified')
    if is_verified is not None:
        wallets = wallets.filter(is_verified=is_verified == 'true')
    
    paginator = Paginator(wallets, 20)
    page = request.GET.get('page')
    wallets = paginator.get_page(page)
    
    return render(request, 'staff/payment/wallet_list.html', {
        'wallets': wallets
    })

@login_required
@staff_required
def pi_wallet_detail(request, pk):
    """View Pi wallet details and transactions"""
    wallet = get_object_or_404(PiWallet, pk=pk)
    transactions = wallet.pitransaction_set.select_related('order').all()[:10]
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_verification':
            wallet.is_verified = not wallet.is_verified
            wallet.save()
            
            # Log activity
            ActivityLog.objects.create(
                staff=request.user.staffmember,
                action='update',
                content_type='wallet',
                object_id=pk,
                description=f'{"Verified" if wallet.is_verified else "Unverified"} wallet for {wallet.user.email}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Wallet verification status updated successfully.')
            return redirect('staff:pi_wallet_detail', pk=pk)
    
    return render(request, 'staff/payment/wallet_detail.html', {
        'wallet': wallet,
        'transactions': transactions
    })

@login_required
@staff_required
def delete_product_image(request, pk):
    """Delete a product's additional image"""
    if request.method == 'POST':
        try:
            image = ProductImages.objects.get(pk=pk)
            image.delete()
            return JsonResponse({'success': True})
        except ProductImages.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
