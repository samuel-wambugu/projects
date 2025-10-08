from .models import CustomUser, Tutorial, Comments
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

class MyCustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['fullname', 'email', 'phonenumber']

class TutorialForm(ModelForm):
    class Meta:
        model = Tutorial
        fields = ['title', 'content', 'thumbnail', 'video', 'video_url', 'price', 'free_access', 'level', 'order']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].widget.attrs['min'] = '0'  # Ensure price is not negative
        self.fields['price'].help_text = 'Set to 0 if tutorial is free'

class CommentsForm(ModelForm):
    class Meta:
        model = Comments
        fields = ['body', 'tutorial']