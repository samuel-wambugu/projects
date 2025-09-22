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
        email = request.POST.get('Email').lower()
        password = request.POST.get('Password')

        
        
        user = authenticate(request, username=email, password=password)

    

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "username or password doesn't exist")
    


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
            messages.error(request, 'the user already exist')
        elif CustomUser.objects.filter(phonenumber=contact).exists():
            messages.error(request, 'the contact already exist')
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

        video = MediaFiles.objects.create(title=title, videos=video_file)
        return JsonResponse({
            "message": "Video uploaded successfully!",
            "video_url" : video.videos.url,
            "title" : video.title
        })
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def upload_thumbnail(request):
    if  request.method == "POST":
        image = request.FILES.get('images')
        if image:
            Thumbnail.objects.create(cover=image)
    return render(request, 'base/dashboard.html')






