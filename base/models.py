from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    Categories = [
        ('work', 'Work'),
        ('personal', 'Personal'),
        ('shopping', 'Shopping'),
        ('health', 'Health'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200, help_text="Task title", blank=True, default='')
    description = models.TextField(blank=True, null=True, help_text="Task description")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    complete = models.BooleanField(default=False, help_text="Mark as complete")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(help_text="Set the due date", blank=True, null=True)
    categories = models.CharField(max_length=20, choices=Categories, default='other')
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title if hasattr(self, 'title') and self.title else (self.description[:50] if self.description else "Unnamed Task")
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and not self.complete:
            return self.due_date < timezone.now().date()
        return False
    
    @property
    def tag_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

