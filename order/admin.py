from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem, OrderStatusHistory

class CartItemInline(admin.TabularInline):
    model = CartItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'shipping_name', 'status', 'total_amount', 'created_at', 'payment_status']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['id', 'user__email', 'shipping_name', 'shipping_address']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            obj.update_status(obj.status, user=request.user)
        super().save_model(request, obj, form, change)
