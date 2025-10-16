from django.contrib import admin
from .models import CustomUser, Tutorial, Subscription, CurrencyPair, UserProgress, SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_ksh', 'duration_days', 'is_active', 'updated_at']
    list_filter = ['is_active', 'name']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


admin.site.register(CustomUser)
admin.site.register(Tutorial)
admin.site.register(Subscription)
admin.site.register(CurrencyPair)
admin.site.register(UserProgress)

# admin.site.register(Comments)
# admin.site.register(MediaFiles)
# admin.site.register(Thumbnail)





        
