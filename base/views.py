from django.shortcuts import render , get_object_or_404, redirect
from .models import Comments , CustomUser , MediaFiles, Thumbnail
from django.contrib.auth import logout, login, authenticate
from .form import CommentsForm, MyCustomUserForm, MediaFilesForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def dashboard(request,):
    user = CustomUser.objects.all()
    video = MediaFiles.objects.all()
    context = {'user': user, 'video':video}

    return render(request, 'base/dashboard.html',context)

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






