from .models import CustomUser, Comments, MediaFiles
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

class MyCustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['fullname', 'email', 'phonenumber']

class CommentsForm(ModelForm):
    class Meta:
        model = Comments
        fields = '__all__'

class MediaFilesForm(ModelForm):
    class Meta:
        model = MediaFiles
        fields = '__all__'