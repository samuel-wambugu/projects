from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Task
from .forms import TaskForm, customizedUserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta



def home(request):
    return render(request, 'base/home.html')

@login_required(login_url='/')
def userpage(request):
    tasks = Task.objects.filter(user=request.user)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Filter functionality
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    category_filter = request.GET.get('category', '')
    if category_filter:
        tasks = tasks.filter(categories=category_filter)
    
    # Sorting functionality
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['due_date', '-due_date', 'priority', '-priority', 'created_at', '-created_at', 'title', '-title']
    if sort_by in valid_sorts:
        tasks = tasks.order_by(sort_by)
    
    # Statistics
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, complete=True).count()
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = Task.objects.filter(
        user=request.user,
        complete=False,
        due_date__lt=timezone.now().date()
    ).count()
    
    context = {
        'tasks': tasks,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'sort_by': sort_by,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'category_choices': Task.Categories,
    }
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
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('userpage')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm()
    
    context = {'form': form}
    return render(request, 'base/create_task.html', context)


@login_required(login_url='/')
def edit_task(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_details', pk=task.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm(instance=task)
    
    context = {'form': form, 'task': task}
    return render(request, 'base/edit_task.html', context)


def create_account(request):
    
    if request.method == 'POST': 
        username = request.POST.get('username').lower()
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirmpassword')
        if password != confirm:
            messages.error(request, "the password doesnot match")
        elif User.objects.filter(username = username).exists():
            messages.error(request,"user already exist")
        elif User.objects.filter(email= email).exists():
            messages.error(request, "the email already exist")
        else:
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
            )
            login(request, user)
            return redirect('userpage')


    return render(request, 'base/create_account.html')


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


@login_required(login_url='/')
def toggle_complete(request, pk):
    """Toggle task completion status via AJAX"""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=pk, user=request.user)
        task.complete = not task.complete
        if task.complete:
            task.status = 'completed'
        else:
            task.status = 'todo'
        task.save()
        return JsonResponse({
            'success': True,
            'complete': task.complete,
            'status': task.get_status_display()
        })
    return JsonResponse({'success': False}, status=400)


@login_required(login_url='/')
def dashboard(request):
    """Dashboard with task statistics and analytics"""
    user_tasks = Task.objects.filter(user=request.user)
    
    # Basic statistics
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(complete=True).count()
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = user_tasks.filter(
        complete=False,
        due_date__lt=timezone.now().date()
    ).count()
    
    # Completion rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Tasks by priority
    high_priority = user_tasks.filter(priority='high').count()
    medium_priority = user_tasks.filter(priority='medium').count()
    low_priority = user_tasks.filter(priority='low').count()
    
    # Tasks by category
    tasks_by_category = user_tasks.values('categories').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Tasks by status
    tasks_by_status = user_tasks.values('status').annotate(
        count=Count('id')
    )
    
    # Recent tasks
    recent_tasks = user_tasks.order_by('-created_at')[:5]
    
    # Upcoming tasks (next 7 days)
    upcoming_tasks = user_tasks.filter(
        complete=False,
        due_date__gte=timezone.now().date(),
        due_date__lte=timezone.now().date() + timedelta(days=7)
    ).order_by('due_date')[:5]
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'completion_rate': round(completion_rate, 1),
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'tasks_by_category': tasks_by_category,
        'tasks_by_status': tasks_by_status,
        'recent_tasks': recent_tasks,
        'upcoming_tasks': upcoming_tasks,
    }
    return render(request, 'base/dashboard.html', context)