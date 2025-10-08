from django.urls import path
from . import views


urlpatterns = [
    # Authentication URLs
    path('', views.home, name='home'),  # Landing page
    path('accounts/login/', views.loginfunc, name='login'),  # Match Django's default login URL
    path('accounts/logout/', views.logoutpage, name='logout'),
    path('accounts/register/', views.register, name='register'),
    
    # Main app URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload-video/', views.upload_video, name='upload_video'),
    path('upload-thumbnail/', views.upload_thumbnail, name='upload_thumbnail'),
    
    # Tutorial URLs
    path('tutorials/', views.tutorial_list, name='tutorial_list'),
    path('tutorials/<int:pk>/', views.tutorial_detail, name='tutorial_detail'),
    path('tutorials/<int:pk>/complete/', views.mark_tutorial_complete, name='mark_tutorial_complete'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tutorials/create/', views.create_tutorial, name='create_tutorial'),
    
    # Subscription URLs
    path('subscriptions/', views.subscription_plans, name='subscription_plans'),
    path('subscriptions/payment/', views.initiate_payment, name='initiate_payment'),
    
    # Forex URLs
    path('forex/', views.forex_dashboard, name='forex_dashboard'),
    path('forex/chart/<int:pair_id>/', views.forex_chart, name='forex_chart'),
]
