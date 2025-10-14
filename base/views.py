from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Comments, CustomUser, Tutorial, Subscription, CurrencyPair, UserProgress, SubscriptionPlan
from django.contrib.auth import logout, login, authenticate
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import timedelta
from django.utils.decorators import method_decorator
from functools import wraps
from .form import MyCustomUserForm, TutorialForm, SubscriptionPlanForm
import json

from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.utils.decorators import method_decorator

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator

def superuser_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a superuser.
    Redirects to login page if not authenticated.
    Returns 403 if authenticated but not superuser.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse('login')
            return redirect(f"{login_url}?next={request.path}")
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view
    
def api_superuser_required(view_func):
    """
    Decorator for API views that checks that the user is logged in and is a superuser.
    Returns appropriate JSON responses for each case.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Please log in"}, status=401)
        if not request.user.is_superuser:
            return JsonResponse({"error": "Unauthorized"}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Import M-Pesa integration
try:
    from django_daraja.mpesa.core import MpesaClient
    MPESA_ENABLED = True
except ImportError:
    MPESA_ENABLED = False
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import json


# Create your views here.

def home(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    featured_tutorials = Tutorial.objects.filter(is_featured=True)[:3]
    context = {
        'featured_tutorials': featured_tutorials,
    }
    return render(request, 'base/home.html', context)

@login_required
def dashboard(request):
    user = request.user
    subscription = Subscription.objects.filter(user=user, is_active=True).first()
    tutorials = Tutorial.objects.all().order_by('order')  # Ensure consistent ordering
    currency_pairs = CurrencyPair.objects.all()
    user_progress = UserProgress.objects.filter(user=user)
    
    # Calculate progress
    total_tutorials = tutorials.count()
    completed_tutorials = user_progress.filter(completed=True).count()
    progress_percentage = (completed_tutorials / total_tutorials * 100) if total_tutorials > 0 else 0
    
    context = {
        'user': user,
        'subscription': subscription,
        'tutorials': tutorials,
        'currency_pairs': currency_pairs,
        'progress_percentage': progress_percentage,
        'total_tutorials': total_tutorials,
        'completed_tutorials': completed_tutorials,
    }
    
    # Add superuser-specific context
    if user.is_superuser:
        # Get engagement metrics
        total_users = CustomUser.objects.count()
        total_students = UserProgress.objects.values('user').distinct().count()
        active_subscriptions = Subscription.objects.filter(is_active=True).count()
        total_earnings = sum(tutorial.price for tutorial in tutorials if not tutorial.free_access)
        all_user_progress = UserProgress.objects.all()
        
        # Calculate overall platform engagement
        total_completions = all_user_progress.filter(completed=True).count()
        avg_completion_rate = (total_completions / (total_users * total_tutorials) * 100) if total_users > 0 and total_tutorials > 0 else 0
        
        # Get tutorial-specific engagement
        tutorial_stats = []
        for tutorial in tutorials:
            completions = all_user_progress.filter(tutorial=tutorial, completed=True).count()
            completion_rate = (completions / total_users * 100) if total_users > 0 else 0
            tutorial_stats.append({
                'tutorial': tutorial,
                'completions': completions,
                'completion_rate': completion_rate,
            })
        
        # Add superuser context
        context.update({
            'total_users': total_users,
            'total_students': total_students,
            'active_subscriptions': active_subscriptions,
            'total_earnings': total_earnings,
            'avg_completion_rate': avg_completion_rate,
            'tutorial_stats': tutorial_stats,
            'show_all_tutorials': True,  # Flag to show all tutorials regardless of subscription
        })
    return render(request, 'base/dashboard.html', context)

def loginfunc(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('Email', '').lower().strip()
        password = request.POST.get('Password', '')

        if not email or not password:
            messages.error(request, "Please provide both email and password")
            return render(request, 'base/loginpage.html', {'page': page})

        # Check if user exists first
        if not CustomUser.objects.filter(email=email).exists():
            messages.error(request, "No account found with this email")
            return render(request, 'base/loginpage.html', {'page': page})
            
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, "This account is inactive")
        else:
            messages.error(request, "Invalid password")


    return render(request, 'base/loginpage.html', {'page':page})

def logoutpage(request):
    logout(request)
    return redirect('login')

@login_required
def tutorial_list(request):
    tutorials = Tutorial.objects.all()
    user_progress = UserProgress.objects.filter(user=request.user)
    subscription = Subscription.objects.filter(user=request.user, is_active=True).first()
    
    # Show all tutorials in the list (so users can see what's available)
    # Access control is handled in individual tutorial detail views
    
    context = {
        'tutorials': tutorials,
        'user_progress': user_progress,
        'subscription': subscription
    }
    return render(request, 'base/tutorial_list.html', context)

@login_required
def tutorial_detail(request, pk):
    tutorial = get_object_or_404(Tutorial, pk=pk)
    subscription = Subscription.objects.filter(user=request.user, is_active=True).first()
    
    # Check access permission - Premium tutorials require subscription or payment
    # For now, we'll just check if tutorial costs money and user doesn't have subscription
    # TODO: Add individual purchase tracking model later
    
    if not request.user.is_superuser and tutorial.price > 0 and not tutorial.free_access and not subscription:
        # Instead of redirecting, show the tutorial with purchase modal
        print(f"DEBUG: Showing purchase modal for {tutorial.title}, Price: {tutorial.price}, User: {request.user}")  # Debug line
        
        # Get next and previous tutorials for navigation
        next_tutorial = Tutorial.objects.filter(id__gt=tutorial.id).order_by('id').first()
        prev_tutorial = Tutorial.objects.filter(id__lt=tutorial.id).order_by('-id').first()
        
        context = {
            'tutorial': tutorial,
            'show_purchase_modal': True,
            'subscription': subscription,
            'next_tutorial': next_tutorial,
            'prev_tutorial': prev_tutorial,
            'is_superuser': request.user.is_superuser
        }
        return render(request, 'base/tutorial_detail.html', context)
    
    # Track progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        tutorial=tutorial
    )
    if not progress.completed:
        progress.last_accessed = timezone.now()
        progress.save()
    
    # Get next and previous tutorials
    next_tutorial = Tutorial.objects.filter(id__gt=tutorial.id).order_by('id').first()
    prev_tutorial = Tutorial.objects.filter(id__lt=tutorial.id).order_by('-id').first()
    
    context = {
        'tutorial': tutorial,
        'progress': progress,
        'next_tutorial': next_tutorial,
        'prev_tutorial': prev_tutorial,
        'subscription': subscription,
        'is_superuser': request.user.is_superuser
    }
    return render(request, 'base/tutorial_detail.html', context)

@login_required
def mark_tutorial_complete(request, pk):
    tutorial = get_object_or_404(Tutorial, pk=pk)
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        tutorial=tutorial
    )
    progress.completed = True
    progress.completion_date = timezone.now()
    progress.save()
    
    messages.success(request, f"Congratulations! You've completed {tutorial.title}")
    return redirect('tutorial_list')

@login_required
def subscription_plans(request):
    # Get active subscription plans from the database
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('duration_days')
    
    context = {
        'current_subscription': Subscription.objects.filter(
            user=request.user,
            is_active=True
        ).first(),
        'plans': plans,
    }
    return render(request, 'base/subscription_plans.html', context)

@login_required
def forex_dashboard(request):
    # Fetch latest forex data
    # from .services import fetch_forex_data
    # fetch_forex_data()  # Temporarily disabled - requires yfinance
    
    # Get all currency pairs
    currency_pairs = CurrencyPair.objects.all().order_by('base_currency')
    
    context = {
        'currency_pairs': currency_pairs
    }
    return render(request, 'base/forex_dashboard.html', context)

@login_required
def forex_chart(request, pair_id):
    # from .services import get_forex_chart_data  # Temporarily disabled - requires yfinance
    
    pair = get_object_or_404(CurrencyPair, id=pair_id)
    timeframe = request.GET.get('timeframe', '1mo')
    
    # chart_data = get_forex_chart_data(pair_id, timeframe)  # Temporarily disabled
    chart_data = {}  # Empty chart data for now
    
    context = {
        'pair': pair,
        'chart_data': chart_data,
        'timeframe': timeframe
    }
    return render(request, 'base/forex_chart.html', context)

@login_required
def initiate_payment(request):
    if not MPESA_ENABLED:
        messages.error(request, 'Payment system is currently unavailable')
        return redirect('subscription_plans')
        
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        amount = request.POST.get('amount')
        subscription_type = request.POST.get('subscription_type')
        
        if not all([phone_number, amount, subscription_type]):
            messages.error(request, 'Please provide all required information')
            return redirect('subscription_plans')
            
        try:
            cl = MpesaClient()
            phone_number = phone_number.replace('+', '')  # Remove + from phone number
            
            # Initiate STK push
            response = cl.stk_push(
                phone_number=phone_number,
                amount=int(float(amount)),
                account_reference='Forex Tutorial',
                transaction_desc=f'{subscription_type} Subscription Payment'
            )
            
            if 'CheckoutRequestID' in response:
                # Store payment information
                request.session['pending_payment'] = {
                    'checkout_request_id': response['CheckoutRequestID'],
                    'subscription_type': subscription_type,
                    'amount': amount
                }
                messages.success(request, 'Payment initiated. Please complete the payment on your phone.')
            else:
                messages.error(request, 'Payment initiation failed. Please try again.')
                
        except Exception as e:
            messages.error(request, f'Payment processing error: {str(e)}')
            
    return redirect('subscription_plans')

@csrf_exempt
def mpesa_callback(request):
    """
    Handle M-Pesa STK Push callback
    This endpoint receives payment notifications from Safaricom
    """
    if request.method == 'POST':
        try:
            # Process the callback data
            data = json.loads(request.body)
            
            # Log callback for debugging (remove in production)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'M-Pesa Callback received: {data}')
            
            # Validate required fields
            if not all(key in data for key in ['Body']):
                return HttpResponse('OK')  # Return OK to acknowledge receipt
            
            callback = data.get('Body', {}).get('stkCallback', {})
            if not callback or 'ResultCode' not in callback:
                return HttpResponse('OK')
            
            # Check if payment was successful
            if callback['ResultCode'] == 0:
                checkout_request_id = callback['CheckoutRequestID']
                
                # Get pending payment info from session
                pending_payment = request.session.get('pending_payment', {})
                if pending_payment.get('checkout_request_id') == checkout_request_id:
                    # Create subscription
                    subscription_type = pending_payment['subscription_type']
                    amount = pending_payment['amount']
                    
                    # Calculate end date based on subscription type
                    duration_map = {
                        'monthly': 30,
                        'quarterly': 90,
                        'yearly': 365
                    }
                    days = duration_map.get(subscription_type, 30)
                    end_date = timezone.now() + timedelta(days=days)
                    
                    Subscription.objects.create(
                        user=request.user,
                        subscription_type=subscription_type,
                        end_date=end_date,
                        payment_reference=checkout_request_id,
                        amount_paid=amount
                    )
                    
                    # Clear pending payment
                    del request.session['pending_payment']
                    
                    messages.success(request, 'Payment successful! Your subscription is now active.')
                    
                return HttpResponse('OK')
            else:
                # Payment failed or cancelled
                logger.warning(f'Payment failed with code: {callback["ResultCode"]}')
                return HttpResponse('OK')
            
        except json.JSONDecodeError:
            logger.error('Invalid JSON in M-Pesa callback')
            return HttpResponse('OK')
        except Exception as e:
            logger.error(f'M-Pesa callback error: {str(e)}')
            return HttpResponse('OK')
            
    return HttpResponse('OK')

@csrf_exempt
def mpesa_timeout(request):
    """
    Handle M-Pesa timeout notifications
    Called when customer doesn't complete payment in time
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'M-Pesa Timeout: {data}')
            return HttpResponse('OK')
        except Exception as e:
            return HttpResponse('OK')
    return HttpResponse('OK')

@login_required
def purchase_single_tutorial(request):
    """Handle individual tutorial purchases via M-Pesa"""
    if request.method == 'POST':
        tutorial_id = request.POST.get('tutorial_id')
        phone_number = request.POST.get('phone_number')
        
        if not tutorial_id or not phone_number:
            messages.error(request, 'Please provide all required information')
            return redirect('tutorial_detail', pk=tutorial_id or 1)
        
        try:
            tutorial = get_object_or_404(Tutorial, id=tutorial_id)
            
            if not MPESA_ENABLED:
                messages.error(request, 'Payment system is currently unavailable')
                return redirect('tutorial_detail', pk=tutorial_id)
            
            # Process M-Pesa payment
            cl = MpesaClient()
            phone_number = phone_number.replace('+', '').strip()
            
            # Ensure phone number is in correct format
            if not phone_number.startswith('254'):
                if phone_number.startswith('0'):
                    phone_number = '254' + phone_number[1:]
                else:
                    phone_number = '254' + phone_number
            
            # Initiate STK push for individual tutorial
            account_reference = f"Tutorial_{tutorial.id}_{request.user.id}"
            transaction_desc = f"Purchase: {tutorial.title}"
            
            response = cl.stk_push(
                phone_number=phone_number,
                amount=int(tutorial.price),
                account_reference=account_reference,
                transaction_desc=transaction_desc,
                callback_url="https://yourdomain.com/mpesa/callback/"  # Update with your actual domain
            )
            
            if response and response.get('ResponseCode') == '0':
                messages.success(request, f'Payment request sent to {phone_number}. Please complete the payment on your phone.')
                
                # Store pending payment info (you might want to create a PendingPayment model)
                # For now, we'll use session storage
                request.session[f'pending_tutorial_purchase_{tutorial.id}'] = {
                    'phone_number': phone_number,
                    'amount': float(tutorial.price),
                    'timestamp': timezone.now().isoformat()
                }
            else:
                messages.error(request, 'Failed to initiate payment. Please try again.')
                
        except Tutorial.DoesNotExist:
            messages.error(request, 'Tutorial not found')
        except Exception as e:
            messages.error(request, f'Payment processing error: {str(e)}')
    
    return redirect('tutorial_detail', pk=tutorial_id)

def register(request):
    
    if request.method == 'POST':
        fullname = request.POST.get('fullname').lower()
        email = request.POST.get('Email').lower()
        contact = request.POST.get('Contact')
        password = request.POST.get('Password')
        password1 = request.POST.get('Password1')

        if password != password1:
            messages.error(request, 'the password doesnot match')
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
        elif CustomUser.objects.filter(phonenumber=contact).exists():
            messages.error(request, 'Phone number already exists')
        else:
            user = CustomUser.objects.create_user(
                fullname=fullname,
                email=email,
                phonenumber=contact,
                password= password
            )
            login(request,user)
            return redirect('dashboard')

        
    return render(request, 'base/loginpage.html')


@login_required
@superuser_required


@superuser_required
def create_tutorial(request):
    """Create new tutorial view"""
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES)
        if form.is_valid():
            tutorial = form.save(commit=False)
            tutorial.author = request.user
            tutorial.free_access = form.cleaned_data.get('free_access', False)
            tutorial.price = 0 if tutorial.free_access else form.cleaned_data.get('price', 0)
            tutorial.order = form.cleaned_data.get('order', Tutorial.objects.count() + 1)
            
            if 'video' in request.FILES:
                tutorial.video = request.FILES['video']
            if 'thumbnail' in request.FILES:
                tutorial.thumbnail = request.FILES['thumbnail']
            
            tutorial.save()
            messages.success(request, f'Tutorial "{tutorial.title}" has been created successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
            
        # Add context for superuser dashboard
        context = {
            'form': form,
            'total_tutorials': Tutorial.objects.count(),
            'total_students': CustomUser.objects.count(),
        }
        
        return render(request, 'base/tutorial_form.html', context)
    
    form = TutorialForm()
    
    # Add context for superuser dashboard
    context = {
        'form': form,
        'total_tutorials': Tutorial.objects.count(),
        'total_students': CustomUser.objects.count(),
    }
    
    return render(request, 'base/tutorial_form.html', context)

@csrf_exempt
@superuser_required
def upload_video(request):        
    if request.method == "POST" and request.FILES.get("video"):
        title = request.POST.get("title", "Untitled")
        video_file = request.FILES["video"]
        thumbnail = request.FILES.get("thumbnail")
        price = request.POST.get("price", 0)
        free_access = request.POST.get("free_access", "false").lower() == "true"
        
        tutorial = Tutorial.objects.create(
            author=request.user,
            title=title,
            video=video_file,
            thumbnail=thumbnail if thumbnail else None,
            content="",  # Add default content or get from request
            price=price if not free_access else 0,
            free_access=free_access,
            order=Tutorial.objects.count() + 1  # Default ordering at the end
        )
        
        return JsonResponse({
            "message": "Video uploaded successfully!",
            "video_url": tutorial.video.url,
            "title": tutorial.title,
            "thumbnail_url": tutorial.thumbnail.url if tutorial.thumbnail else None,
            "price": float(tutorial.price)
        })
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def upload_thumbnail(request):
    if request.method == "POST" and request.FILES.get('thumbnail'):
        image = request.FILES['thumbnail']
        tutorial_id = request.POST.get('tutorial_id')
        
        if tutorial_id:
            try:
                tutorial = Tutorial.objects.get(id=tutorial_id)
                tutorial.thumbnail.save(image.name, image, save=True)
                tutorial.save()
                
                return JsonResponse({
                    "message": "Thumbnail uploaded successfully!",
                    "thumbnail_url": tutorial.thumbnail.url
                })
            except Tutorial.DoesNotExist:
                return JsonResponse({"error": "Tutorial not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
@user_passes_test(lambda u: u.is_superuser)
@login_required
@superuser_required
def delete_tutorial(request, tutorial_id):
    if request.method == 'POST':
        try:
            tutorial = get_object_or_404(Tutorial, id=tutorial_id)
            title = tutorial.title
            tutorial.delete()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': f'Tutorial "{title}" has been deleted successfully.'
                })
            messages.success(request, f'Tutorial "{title}" has been deleted successfully.')
            return redirect('dashboard')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=400)
            messages.error(request, f'Error deleting tutorial: {str(e)}')
            return redirect('dashboard')
    return HttpResponseRedirect(reverse('dashboard'))


# Subscription Plan Management Views
@superuser_required
def manage_subscription_plans(request):
    """View for superusers to manage subscription plans"""
    plans = SubscriptionPlan.objects.all().order_by('duration_days')
    
    # Check if all three plan types exist
    existing_plan_types = list(plans.values_list('name', flat=True))
    all_plan_types = ['monthly', 'quarterly', 'yearly']
    available_plan_types = [pt for pt in all_plan_types if pt not in existing_plan_types]
    
    context = {
        'plans': plans,
        'total_plans': plans.count(),
        'active_plans': plans.filter(is_active=True).count(),
        'can_create_more': len(available_plan_types) > 0,
        'max_plans_reached': plans.count() >= 3,
    }
    
    return render(request, 'base/manage_subscription_plans.html', context)


@superuser_required
def create_subscription_plan(request):
    """Create new subscription plan"""
    # Check if all three plans already exist
    if SubscriptionPlan.objects.count() >= 3:
        messages.warning(request, 'All three subscription plans (Monthly, Quarterly, Yearly) already exist. You can only edit existing plans.')
        return redirect('manage_subscription_plans')
    
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Subscription plan "{plan.get_name_display()}" created successfully!')
            return redirect('manage_subscription_plans')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SubscriptionPlanForm()
    
    return render(request, 'base/subscription_plan_form.html', {
        'form': form,
        'action': 'Create',
    })


@superuser_required
def edit_subscription_plan(request, plan_id):
    """Edit existing subscription plan"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST, instance=plan)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Subscription plan "{plan.get_name_display()}" updated successfully!')
            return redirect('manage_subscription_plans')
    else:
        form = SubscriptionPlanForm(instance=plan)
    
    return render(request, 'base/subscription_plan_form.html', {
        'form': form,
        'action': 'Edit',
        'plan': plan,
    })


@superuser_required
def delete_subscription_plan(request, plan_id):
    """Delete subscription plan"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    plan_name = plan.get_name_display()
    
    plan.delete()
    messages.success(request, f'Subscription plan "{plan_name}" deleted successfully!')
    
    return redirect('manage_subscription_plans')


@superuser_required
def toggle_plan_status(request, plan_id):
    """Toggle subscription plan active status"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    plan.is_active = not plan.is_active
    plan.save()
    
    status = "activated" if plan.is_active else "deactivated"
    messages.success(request, f'Subscription plan "{plan.get_name_display()}" has been {status}!')
    
    return redirect('manage_subscription_plans')


@superuser_required
def manage_users(request):
    """View all registered users with management options"""
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Calculate stats for each user
    user_stats = []
    for user in users:
        if not user.is_superuser:  # Don't show superuser accounts in the list
            subscription = Subscription.objects.filter(user=user, is_active=True).first()
            total_progress = UserProgress.objects.filter(user=user).count()
            completed_tutorials = UserProgress.objects.filter(user=user, completed=True).count()
            
            # Calculate progress percentage for display
            progress_percentage = 0
            if total_progress > 0:
                progress_percentage = int((completed_tutorials / total_progress) * 100)
            
            user_stats.append({
                'user': user,
                'subscription': subscription,
                'total_progress': total_progress,
                'completed_tutorials': completed_tutorials,
                'progress_percentage': progress_percentage,
                'is_active': user.is_active,
            })
    
    context = {
        'user_stats': user_stats,
        'total_users': len(user_stats),
        'active_users': sum(1 for stat in user_stats if stat['is_active']),
        'inactive_users': sum(1 for stat in user_stats if not stat['is_active']),
        'subscribed_users': sum(1 for stat in user_stats if stat['subscription']),
    }
    
    return render(request, 'base/manage_users.html', context)


@superuser_required
def toggle_user_status(request, user_id):
    """Activate or deactivate a user account"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent superuser from deactivating themselves
    if user.id == request.user.id:
        messages.error(request, "You cannot deactivate your own account!")
        return redirect('manage_users')
    
    # Prevent deactivating other superusers
    if user.is_superuser:
        messages.error(request, "You cannot deactivate other superuser accounts!")
        return redirect('manage_users')
    
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f'User "{user.fullname}" ({user.email}) has been {status}!')
    
    return redirect('manage_users')


@superuser_required
def delete_user(request, user_id):
    """Delete a user account permanently"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent superuser from deleting themselves
    if user.id == request.user.id:
        messages.error(request, "You cannot delete your own account!")
        return redirect('manage_users')
    
    # Prevent deleting other superusers
    if user.is_superuser:
        messages.error(request, "You cannot delete other superuser accounts!")
        return redirect('manage_users')
    
    user_name = user.fullname
    user_email = user.email
    user.delete()
    
    messages.success(request, f'User "{user_name}" ({user_email}) has been permanently deleted!')
    
    return redirect('manage_users')


@superuser_required
def user_detail(request, user_id):
    """View detailed information about a specific user"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Get user's subscription info
    current_subscription = Subscription.objects.filter(user=user, is_active=True).first()
    subscription_history = Subscription.objects.filter(user=user).order_by('-start_date')
    
    # Get user's tutorial progress
    user_progress = UserProgress.objects.filter(user=user).select_related('tutorial')
    completed_count = user_progress.filter(completed=True).count()
    total_tutorials = Tutorial.objects.count()
    completion_percentage = (completed_count / total_tutorials * 100) if total_tutorials > 0 else 0
    
    context = {
        'viewed_user': user,
        'current_subscription': current_subscription,
        'subscription_history': subscription_history,
        'user_progress': user_progress,
        'completed_count': completed_count,
        'total_tutorials': total_tutorials,
        'completion_percentage': completion_percentage,
    }
    
    return render(request, 'base/user_detail.html', context)