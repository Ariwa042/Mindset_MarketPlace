from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        
        # Remove username from extra_fields if it exists
        if 'username' in extra_fields:
            del extra_fields['username']
            
        # Generate username from email
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        
        # Ensure username uniqueness
        while self.model.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Create user with generated username
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=32, unique=True, null=True, blank=True)  # Make optional
    first_name = models.CharField(max_length=30, blank=True, null=True)  # Make required
    last_name = models.CharField(max_length=30, blank=True, null=True)   # Make required

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Remove username from required fields

    objects = CustomUserManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_shipping_name(self):
        return self.get_full_name()

    def get_profile(self):
        return self.profile

    def __str__(self):
        return self.email  # Use email instead of username

    class Meta:
        verbose_name = 'CustomUser'
        verbose_name_plural = 'CustomUsers'

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    default_shipping_address = models.TextField(blank=True)
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

