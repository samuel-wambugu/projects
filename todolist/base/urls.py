from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('Create-account/', views.create_account, name='create_account'),
    path('userpage/', views.userpage, name="userpage"),
    path('task_details/<str:pk>', views.task_details, name="task_details"),
    path('create_task/', views.create_task, name='create_task'),
    path('login/', views.loginAccount, name='loginpage'),
    path('logout/', views.logoutpage, name='logoutpage'),

    path('delete/<str:pk>', views.delete_task, name='delete_task'),
    path('edit_task/<str:pk>', views.edit_task, name='edit_task'),
]
