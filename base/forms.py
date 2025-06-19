from django import forms
from .models import Task
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        feilds = '__all__'
        exclude = ['complete', 'user']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
class customizedUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
