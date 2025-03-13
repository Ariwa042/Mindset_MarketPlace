from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .utils import process_product_image, process_thumbnail

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
   # image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='subcategories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Sub Categories'
        unique_together = ('category', 'slug')
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    )
    
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    specs = models.JSONField(blank=True, null=True)  # For technical specifications
    price = models.DecimalField(max_digits=10, decimal_places=2)
#    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    sales = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    meta_keywords = models.CharField(max_length=255, blank=True)  # For SEO
    meta_description = models.TextField(blank=True)  # For SEO
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def current_price(self):
        return self.price if self.price else self.price

class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta():
       verbose_name_plural = "Product Images"

@receiver(pre_save, sender=Product)
def compress_product_images(sender, instance, **kwargs):
    """Compress product images before saving"""
    if instance.image:
        # Check if image was changed
        try:
            old_instance = Product.objects.get(pk=instance.pk)
            if old_instance.image != instance.image:
                instance.image = process_product_image(instance.image)
        except Product.DoesNotExist:
            # New instance
            instance.image = process_product_image(instance.image)

@receiver(pre_save, sender=ProductImages)
def compress_additional_images(sender, instance, **kwargs):
    """Compress additional product images before saving"""
    if instance.images:
        try:
            old_instance = ProductImages.objects.get(pk=instance.pk)
            if old_instance.images != instance.images:
                instance.images = process_product_image(instance.images)
        except ProductImages.DoesNotExist:
            instance.images = process_product_image(instance.images)