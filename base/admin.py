from django.contrib import admin
from .models import CustomUser,Tutorial, Subscription, CurrencyPair, UserProgress #Comments,MediaFiles,Thumbnail



admin.site.register(CustomUser)
admin.site.register(Tutorial)
admin.site.register(Subscription)
admin.site.register(CurrencyPair)
admin.site.register(UserProgress)

# admin.site.register(Comments)
# admin.site.register(MediaFiles)
# admin.site.register(Thumbnail)





        
