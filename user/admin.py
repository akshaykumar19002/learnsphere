from django.contrib import admin

from .models import UserPreference, Topic, Job, JobTopic

# Register your models here.
admin.site.register(UserPreference)
admin.site.register(Topic)
admin.site.register(Job)
admin.site.register(JobTopic)
