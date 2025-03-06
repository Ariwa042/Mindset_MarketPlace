from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from product.models import Product, Category, SubCategory
from order.models import Order
from .forms import ContactForm
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.db.models import Prefetch

@ensure_csrf_cookie
def home(request):
    """Homepage view with featured products, categories and their subcategories"""
    # Get categories with their active subcategories preloaded
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
        'new_arrivals': Product.objects.filter(
            status='published'
        ).order_by('-created_at')[:4],
        'top_categories': categories,  # Now includes subcategories
        'best_sellers': Product.objects.filter(
            status='published'
        ).order_by('-sales')[:4],
    }
    return render(request, 'core/home.html', context)

class AboutView(TemplateView):
    """About us page view"""
    template_name = 'core/about.html'


@ensure_csrf_cookie
def contact(request):
    """Contact form view with email notification"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            
            # Send email notification
            send_mail(
                subject=f'New Contact Form Submission: {contact_message.subject}',
                message=f'From: {contact_message.name} ({contact_message.email})\n\n{contact_message.message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            
            messages.success(request, 'Thank you for your message. We will get back to you soon!')
            return redirect('core:contact_success')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})

class ContactSuccessView(TemplateView):
    """Success page after contact form submission"""
    template_name = 'core/contact_success.html'
    
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class TermsView(TemplateView):
    """Terms of service page"""
    template_name = 'core/terms.html'

class PrivacyPolicyView(TemplateView):
    """Privacy policy page"""
    template_name = 'core/privacy_policy.html'

class FAQView(TemplateView):
    """FAQ page"""
    template_name = 'core/faq.html'

def handler404(request, exception):
    """Custom 404 error page"""
    return render(request, 'core/404.html', status=404)

def handler500(request):
    """Custom 500 error page"""
    return render(request, 'core/500.html', status=500)

def handler403(request, exception):
    """Custom 403 error page"""
    return render(request, 'core/403.html', status=403)
