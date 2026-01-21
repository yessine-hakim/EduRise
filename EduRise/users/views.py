from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import ProfileEditForm
import logging
import json
import time

logger = logging.getLogger(__name__)


def login_view(request):
    """Handle user login"""
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect to next parameter or default to dashboard
            next_url = request.GET.get('next', 'users:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('users:login')


@login_required
def home(request):
    """Home page view - redirects to dashboard for government/institutional users"""
    return redirect('users:dashboard')


@login_required
def dashboard(request):
    """Dashboard view"""
    return render(request, 'dashboard.html')


@login_required
def profile_edit(request):
    """Edit user profile - supports both AJAX and form submissions"""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if form.is_valid():
            user = form.save()
            
            if is_ajax:
                # Return JSON response for AJAX requests
                response_data = {
                    'success': True,
                    'message': 'Profile updated successfully!',
                    'user': {
                        'full_name': user.get_full_name(),
                        'initials': f"{user.first_name[0] if user.first_name else 'U'}{user.last_name[0] if user.last_name else ''}",
                        'profile_image_url': (user.profile_image.url + f'?v={int(time.time())}') if user.profile_image else None,
                    }
                }
                return JsonResponse(response_data)
            else:
                # Redirect for regular form submissions (fallback, shouldn't normally happen)
                return redirect('users:dashboard')
        else:
            if is_ajax:
                # Return JSON error response for AJAX requests
                errors = {}
                for field, field_errors in form.errors.items():
                    errors[field] = [str(e) for e in field_errors]
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors below.',
                    'errors': errors
                })
            else:
                # Shouldn't reach here normally, but handle gracefully
                messages.error(request, 'Please correct the errors below.')
                return redirect('users:dashboard')
    else:
        # GET request shouldn't normally happen - modal handles editing
        # Redirect to dashboard
        return redirect('users:dashboard') 
