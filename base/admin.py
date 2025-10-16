from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'priority', 'categories', 'due_date', 'complete', 'created_at')
    list_filter = ('status', 'priority', 'categories', 'complete', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'tags')
    list_editable = ('status', 'priority', 'complete')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'complete')
        }),
        ('Categories & Tags', {
            'fields': ('categories', 'tags')
        }),
        ('Dates', {
            'fields': ('due_date', 'created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)