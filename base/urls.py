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
    path('tutorials/create/', views.create_tutorial, name='create_tutorial'),
    path('tutorials/<int:tutorial_id>/delete/', views.delete_tutorial, name='delete_tutorial'),
    
    # Subscription URLs
    path('subscriptions/', views.subscription_plans, name='subscription_plans'),
    path('subscriptions/payment/', views.initiate_payment, name='initiate_payment'),
    path('tutorials/purchase/', views.purchase_single_tutorial, name='purchase_single_tutorial'),
    
    # M-Pesa Payment URLs
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('mpesa/timeout/', views.mpesa_timeout, name='mpesa_timeout'),
    
    # Subscription Plan Management (Superuser only)
    path('subscription-plans/manage/', views.manage_subscription_plans, name='manage_subscription_plans'),
    path('subscription-plans/create/', views.create_subscription_plan, name='create_subscription_plan'),
    path('subscription-plans/<int:plan_id>/edit/', views.edit_subscription_plan, name='edit_subscription_plan'),
    path('subscription-plans/<int:plan_id>/delete/', views.delete_subscription_plan, name='delete_subscription_plan'),
    path('subscription-plans/<int:plan_id>/toggle/', views.toggle_plan_status, name='toggle_plan_status'),
    
    # User Management (Superuser only)
    path('users/manage/', views.manage_users, name='manage_users'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    
    # Forex URLs
    path('forex/', views.forex_dashboard, name='forex_dashboard'),
    path('forex/chart/<int:pair_id>/', views.forex_chart, name='forex_chart'),
]
