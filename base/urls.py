from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.loginfunc, name='login'),
    path('logout/',views.logoutpage, name='logout'),
    path('signup/', views.register, name='register'),
    path("upload-video/", views.upload_video, name="upload_video"),
    path('upload_thumbnail/', views.upload_thumbnail, name='upload_thumbnail'),
]
