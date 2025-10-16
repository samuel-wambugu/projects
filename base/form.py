from .models import CustomUser, Tutorial, Comments, SubscriptionPlan
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms

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
        self.fields['price'].help_text = 'Price in KSh (Set to 0 if tutorial is free)'
        self.fields['price'].label = 'Price (KSh)'
        self.fields['price'].required = False  # Make price not required
    
    def clean(self):
        from decimal import Decimal
        cleaned_data = super().clean()
        free_access = cleaned_data.get('free_access')
        price = cleaned_data.get('price')
        
        # If free access is checked, set price to 0
        if free_access:
            cleaned_data['price'] = Decimal('0.00')
        # If not free and no price provided, default to 0
        elif price is None or price == '':
            cleaned_data['price'] = Decimal('0.00')
            
        return cleaned_data

class CommentsForm(ModelForm):
    class Meta:
        model = Comments
        fields = ['body', 'tutorial']


class SubscriptionPlanForm(ModelForm):
    """Form for superusers to manage subscription plans"""
    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'price_ksh', 'duration_days', 'description', 'is_active']
        labels = {
            'price_ksh': 'Price (KSh)',
            'duration_days': 'Duration (Days)',
            'is_active': 'Active',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter plan description...'}),
            'price_ksh': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'duration_days': forms.NumberInput(attrs={'min': '1'}),
        }
        help_texts = {
            'price_ksh': 'Price in Kenyan Shillings',
            'duration_days': 'Number of days the subscription will be valid',
            'name': 'Choose subscription period (Only one plan per type allowed)',
        }
    
    def clean_name(self):
        """Validate that only one plan per type exists"""
        name = self.cleaned_data.get('name')
        
        # If editing an existing plan, exclude it from the check
        if self.instance and self.instance.pk:
            existing = SubscriptionPlan.objects.filter(name=name).exclude(pk=self.instance.pk)
        else:
            existing = SubscriptionPlan.objects.filter(name=name)
        
        if existing.exists():
            raise forms.ValidationError(
                f"A {name} plan already exists. Please edit the existing plan instead."
            )
        
        return name