from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Comments, CustomUser, Tutorial, Subscription, CurrencyPair, UserProgress
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
from .form import MyCustomUserForm, TutorialForm
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
    tutorials = Tutorial.objects.all()
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
    
    # Filter tutorials based on subscription
    if not subscription:
        tutorials = tutorials.filter(free_access=True)
    
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
    
    # Check access permission
    if not tutorial.free_access and not subscription:
        messages.error(request, "Please subscribe to access this tutorial")
        return redirect('subscription_plans')
    
    # Track progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        tutorial=tutorial
    )
    if not progress.completed:
        progress.last_accessed = timezone.now()
        progress.save()
    
    context = {
        'tutorial': tutorial,
        'progress': progress
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
    context = {
        'current_subscription': Subscription.objects.filter(
            user=request.user,
            is_active=True
        ).first()
    }
    return render(request, 'base/subscription_plans.html', context)

@login_required
def forex_dashboard(request):
    # Fetch latest forex data
    from .services import fetch_forex_data
    fetch_forex_data()
    
    # Get all currency pairs
    currency_pairs = CurrencyPair.objects.all().order_by('base_currency')
    
    context = {
        'currency_pairs': currency_pairs
    }
    return render(request, 'base/forex_dashboard.html', context)

@login_required
def forex_chart(request, pair_id):
    from .services import get_forex_chart_data
    
from django.contrib.auth.decorators import login_required



@login_required
def forex_chart(request, pair_id):
    from .services import get_forex_chart_data
    
    pair = get_object_or_404(CurrencyPair, id=pair_id)
    timeframe = request.GET.get('timeframe', '1mo')
    
    chart_data = get_forex_chart_data(pair_id, timeframe)
    
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
    if request.method == 'POST':
        try:
            # Process the callback data
            data = json.loads(request.body)
            
            # Validate required fields
            if not all(key in data for key in ['Body']):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
            
            callback = data.get('Body', {}).get('stkCallback', {})
            if not callback or 'ResultCode' not in callback:
                return JsonResponse({'status': 'error', 'message': 'Invalid callback format'}, status=400)
            
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
                    
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Payment failed',
                    'code': callback['ResultCode']
                }, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def subscription_plans(request):
    active_subscription = Subscription.objects.filter(
        user=request.user, 
        end_date__gt=timezone.now()
    ).first()
    
    context = {
        'active_subscription': active_subscription,
    }
    return render(request, 'base/subscription_plans.html', context)

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
def admin_dashboard(request):
    tutorials = Tutorial.objects.all().order_by('order')
    total_students = UserProgress.objects.filter(tutorial__in=tutorials).values('user').distinct().count()
    total_earnings = sum(tutorial.price for tutorial in tutorials if not tutorial.free_access)
    
    context = {
        'tutorials': tutorials,
        'total_students': total_students,
        'total_earnings': total_earnings,
    }
    return render(request, 'base/admin_dashboard.html', context)

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
            return redirect('admin_dashboard')
        else:
            print("Form errors:", form.errors)  # Debug print
            
        return render(request, 'base/tutorial_form.html', {'form': form})
    
    form = TutorialForm()
    return render(request, 'base/tutorial_form.html', {'form': form})

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






