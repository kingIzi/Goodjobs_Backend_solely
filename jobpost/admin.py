from django.contrib import admin
from .models import *

admin.site.register(Company)
admin.site.register(JobPost)
admin.site.register(UserProfile)
admin.site.register(JobApplication)
admin.site.register(SavedJobPost)
admin.site.register(JobCategory)