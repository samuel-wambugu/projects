from django.shortcuts import render, get_object_or_404, redirect
from .models import Comments, CustomUser, MediaFiles, Thumbnail, Tutorial, Subscription, CurrencyPair, UserProgress
from django.contrib.auth import logout, login, authenticate
from .form import CommentsForm, MyCustomUserForm, MediaFilesForm
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
    from django_daraja.mpesa.core import MpesaClient
    
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


@csrf_exempt
def upload_video(request):
    if request.method == "POST" and request.FILES.get("video"):
        title = request.POST.get("title", "Untitled")
        video_file = request.FILES["video"]
        thumbnail_id = request.POST.get("images")
        
        try:
            thumbnail = Thumbnail.objects.get(id=thumbnail_id) if thumbnail_id else None
            video = MediaFiles.objects.create(
                title=title,
                videos=video_file,
                images=thumbnail
            )
            return JsonResponse({
                "message": "Video uploaded successfully!",
                "video_url": video.videos.url,
                "title": video.title
            })
        except (Thumbnail.DoesNotExist, ValueError):
            return JsonResponse({"error": "Invalid thumbnail ID"}, status=400)
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def upload_thumbnail(request):
    if  request.method == "POST":
        image = request.FILES.get('images')
        if image:
            Thumbnail.objects.create(cover=image)
    return render(request, 'base/dashboard.html')






