from django.db import models
from django.conf import settings
from order.models import Order
import uuid

class PiWallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    passphrase = models.TextField()  # Store the plain passphrase
    is_verified = models.BooleanField(default=False)
    connected_at = models.DateTimeField(auto_now_add=True)
    last_verified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet for {self.user.email}"

class PiTransaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='pi_transaction')
    wallet = models.ForeignKey(PiWallet, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_hash = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Pi Transaction {self.id} for Order {self.order.id}"
