from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem, Order, OrderItem
from product.models import Product
from payment.models import PiWallet

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'order/cart_detail.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_data = {
            'total_items': cart.get_total_items(),
            'total_price': cart.get_total_price(),
        }
        return JsonResponse(cart_data)
    
    return redirect('order:cart_detail')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = cart_item.cart
        cart_data = {
            'total_items': cart.get_total_items(),
            'total_price': cart.get_total_price(),
        }
        return JsonResponse(cart_data)
    
    return redirect('order:cart_detail')

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
    except ValueError:
        messages.error(request, 'Invalid quantity')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = cart_item.cart
        item_data = {
            'total_cost': cart_item.get_cost(),
            'cart_total': cart.get_total_price(),
            'cart_items': cart.get_total_items(),
        }
        return JsonResponse(item_data)
    
    return redirect('order:cart_detail')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    # Get wallet status
    try:
        wallet = PiWallet.objects.get(user=request.user)
    except PiWallet.DoesNotExist:
        wallet = None
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        contact_phone = request.POST.get('contact_phone')
        
        if shipping_address and contact_phone:
            try:
                order = Order.create_from_cart(cart, shipping_address, contact_phone)
                # Redirect to payment processing
                return redirect('payment:process_payment', order_id=order.id)
            except Exception as e:
                messages.error(request, 'Error processing your order.')
                return redirect('order:checkout')
    
    return render(request, 'order/checkout.html', {
        'cart': cart,
        'wallet': wallet
    })

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related(
        'items', 'status_history'
    ).order_by('-created_at')
    
    context = {
        'orders': orders,
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='pending').count(),
        'completed_orders': orders.filter(status='delivered').count()
    }
    return render(request, 'order/order_list.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order/order_detail.html', {'order': order})

@login_required
def order_history(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    status_history = order.get_status_history()
    estimated_delivery = order.get_estimated_delivery()
    
    context = {
        'order': order,
        'status_history': status_history,
        'estimated_delivery': estimated_delivery,
        'items': order.items.all().select_related('product')
    }
    return render(request, 'order/order_history.html', context)
