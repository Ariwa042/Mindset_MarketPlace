from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import StaffMember

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            staff = StaffMember.objects.get(user=request.user, is_active=True)
            request.staff = staff  # Attach staff member to request
            return view_func(request, *args, **kwargs)
        except StaffMember.DoesNotExist:
            messages.error(request, 'Access Denied: Staff privileges required.')
            return redirect('core:home')
    return _wrapped_view
