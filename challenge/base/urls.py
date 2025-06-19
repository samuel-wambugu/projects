from . import  views
from django.urls import path

urlpatterns = [
    path('question/<str:pk>', views.questioning, name='mainhtml'),

]