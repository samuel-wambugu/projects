from django.db import models
from django.contrib.auth.models import AbstractUser , BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField




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
    email = models.EmailField(blank=False,unique=True)
    phonenumber = PhoneNumberField(unique=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS= ['fullname', 'phonenumber']

    

    def __str__(self):
        return self.fullname
    
class Thumbnail(models.Model):
   cover = models.ImageField(upload_to="images")
   def __str__(self):
        return self.cover.name
    
class MediaFiles(models.Model):
    title = models.CharField(max_length=30,blank=False)

    images = models.OneToOneField(Thumbnail, on_delete=models.CASCADE)
    videos = models.FileField(upload_to='videos')
    bio = models.TextField(blank=False)

class Comments(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    body = models.TextField()
    videoImage = models.ForeignKey(MediaFiles,on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body
    

    
