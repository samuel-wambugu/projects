from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    Categories = [
        ('more important','more important'),
        ('important','important'),
        ('less important','less important'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    complete = models.BooleanField(default=False, help_text="Mark as complete")
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(help_text="Set the due date", blank=True, null=True)
    categories = models.CharField(max_length=20,choices=Categories, blank=True)
    #experience = models.TextField(blank=False, null=False)
    #reasons_for_change = models.CharField(max_length=30,blank=False)


    def __str__(self):
        return self.description or "Unnamed Task"

