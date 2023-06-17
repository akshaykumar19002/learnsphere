from django.contrib import admin

from .models import UserPreference, Topic, Job

# Register your models here.
admin.site.register(UserPreference)
admin.site.register(Topic)
admin.site.register(Job)