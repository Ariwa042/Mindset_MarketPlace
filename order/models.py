from django.db import models
from django.conf import settings
from product.models import Product
import uuid
from django.utils import timezone

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.email}"

    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        self.items.all().delete()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.cart}"

    def get_cost(self):
        return self.product.price * self.quantity

class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_name = models.CharField(max_length=100)  # Add new field
    shipping_address = models.TextField()
    contact_phone = models.CharField(max_length=15)
    payment_status = models.BooleanField(default=False)
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    estimated_delivery_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"

    def get_total_items(self):
        return self.items.count()

    @classmethod
    def create_from_cart(cls, cart, shipping_address=None, contact_phone=None):
        profile = cart.user.profile
        shipping_info = profile.get_shipping_info()
        
        # Calculate estimated delivery date (1 week from now)
        estimated_delivery = timezone.now().date() + timezone.timedelta(days=7)
        
        order = cls.objects.create(
            user=cart.user,
            shipping_name=shipping_info['name'],
            total_amount=cart.get_total_price(),
            shipping_address=shipping_address or shipping_info['address'],
            contact_phone=contact_phone or shipping_info['phone'],
            estimated_delivery_date=estimated_delivery
        )
        
        # Convert cart items to order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        # Clear the cart
        cart.clear()
        return order

    def update_status(self, new_status, user=None, notes=''):
        if new_status != self.status:
            self.status = new_status
            self.save()
            OrderStatusHistory.objects.create(
                order=self,
                status=new_status,
                created_by=user,
                notes=notes
            )

    def get_status_history(self):
        return self.status_history.all()

    def get_estimated_delivery(self):
        """Get estimated delivery date or calculate based on status"""
        if self.estimated_delivery_date:
            return self.estimated_delivery_date
        
        if self.status == 'shipped':
            return timezone.now().date() + timezone.timedelta(days=3)
        elif self.status == 'processing':
            return timezone.now().date() + timezone.timedelta(days=5)
        elif self.status == 'pending':
            return timezone.now().date() + timezone.timedelta(days=7)
        
        return None

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order {self.order.id}"

    def get_total_price(self):
        return self.price * self.quantity

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, related_name='status_history', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Order.ORDER_STATUS)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Order status histories'

    def __str__(self):
        return f"{self.order.id} - {self.status} at {self.created_at}"
