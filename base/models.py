from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError




class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    fullname = models.CharField(max_length=200, blank=False)
    email = models.EmailField(blank=False, unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phonenumber = models.CharField(validators=[phone_regex], max_length=17, unique=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['fullname', 'phonenumber']

    

    def __str__(self):
        return self.fullname
    




class Tutorial(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tutorials', null=True)
    title = models.CharField(max_length=200)
    content = models.TextField(default="")
    thumbnail = models.ImageField(upload_to="images", null=True, blank=True)
    video = models.FileField(upload_to='videos', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True, help_text="Price in Kenyan Shillings (KSh). Leave at 0 for free tutorials.")
    free_access = models.BooleanField(default=False)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} by {self.author.fullname}"

    class Meta:
        ordering = ['order', '-created_at']
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_level_display()})"

class Comments(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    body = models.TextField()
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body

class Subscription(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    payment_reference = models.CharField(max_length=100)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.user.email} - {self.subscription_type}"
    
    def is_valid(self):
        return self.is_active and self.end_date > timezone.now()

class CurrencyPair(models.Model):
    base_currency = models.CharField(max_length=3)
    quote_currency = models.CharField(max_length=3)
    current_rate = models.DecimalField(max_digits=10, decimal_places=4)
    daily_high = models.DecimalField(max_digits=10, decimal_places=4)
    daily_low = models.DecimalField(max_digits=10, decimal_places=4)
    daily_change = models.DecimalField(max_digits=5, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['base_currency', 'quote_currency']
    
    def __str__(self):
        return f"{self.base_currency}/{self.quote_currency}"

class SubscriptionPlan(models.Model):
    """Model to store subscription plans that superusers can manage"""
    PLAN_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    price_ksh = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in Kenyan Shillings")
    duration_days = models.IntegerField(help_text="Duration in days")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_name_display()} - KSh {self.price_ksh}"
    
    class Meta:
        ordering = ['duration_days']


class UserProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'tutorial']
    
    def __str__(self):
        return f"{self.user.email} - {self.tutorial.title}"
