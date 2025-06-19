from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from .models import Task
from .forms import TaskForm,customizedUserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import  login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt



def home(request):
    return render(request, 'base/home.html')

@login_required(login_url='/')
def userpage(request):
    tasks = Task.objects.filter(user=request.user)
        
    context = {'tasks': tasks}
    return render(request, 'base/userpage.html', context)

@login_required(login_url='/')
def task_details(request, pk):
    tasks = get_object_or_404(Task, id=pk)
    context = {'tasks': tasks}
    return render(request, 'base/task_details.html', context) 





@login_required(login_url='/')
def delete_task(request, pk):
    task = Task.objects.get(id=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('userpage')
    context = {'del': task}
    return render(request, 'base/delete.html', context)

@login_required(login_url='/')
def create_task(request):
    tasks = Task.objects.filter(user =request.user)
    form = TaskForm
    choices = Task.Categories
    
    if request.method == 'POST':
        description = request.POST.get('description')
        due_date = request.POST.get('duedate')
        categories = request.POST.get('category')
        Task.objects.create(
            user =request.user,
            description=description,
            due_date=due_date,
            categories = categories
        )
        return redirect('userpage')
    context ={'form': form, 'tasks':tasks,'choices':choices}
    return render(request, 'base/create_task.html', context)


@login_required(login_url='/')
def edit_task(request, pk):
    
    task = Task.objects.get(id=pk)
    form = TaskForm(request.POST, instance=task)
    choices = task.Categories

    if request.method == 'POST':
        task.description = request.POST.get('description')
        task.due_date = request.POST.get('due_date')
        task.categories = request.POST.get('category')

        task.save()
        
        return redirect('task_details', pk=task.id)
    context ={'form': form, 'tasks':task,'choices':choices}
    return render(request, 'base/edit_task.html', context)


def create_account(request):
    form = customizedUserCreationForm()

    if request.method == 'POST': 
        form = customizedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('userpage')
        else:
            messages.error(request, 'an error occured during registration')

    return render(request, 'base/create_account.html',{'form':form})


def loginAccount(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('userpage')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('userpage')
        else:
            messages.error(request, 'username or password is not correct')
    context = {'page':page}
    return render(request, 'base/create_account.html',context)

@login_required(login_url='/')
def logoutpage(request):
    logout(request)
    return redirect('home')