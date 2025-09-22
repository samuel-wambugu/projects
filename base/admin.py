from django.contrib import admin
from .models import Comments,CustomUser,MediaFiles,Thumbnail



admin.site.register(CustomUser)
admin.site.register(Comments)
admin.site.register(MediaFiles)
admin.site.register(Thumbnail)





        
