from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=32, unique=True)
    first_name = models.CharField(max_length=30, blank=False)  # Make required
    last_name = models.CharField(max_length=30, blank=False)   # Make required

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Add to required fields

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_shipping_name(self):
        return self.get_full_name()

    def get_profile(self):
        return self.profile

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'CustomUser'
        verbose_name_plural = 'CustomUsers'

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    default_shipping_address = models.TextField(blank=True)
 #   account_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.email}"

    def get_shipping_info(self):
        return {
            'name': self.user.get_full_name(),
            'address': self.default_shipping_address,
            'phone': self.phone_number
        }

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class OTP(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return self.expires_at > timezone.now()

