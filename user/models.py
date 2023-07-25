from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Job(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    topics = models.ManyToManyField(Topic)
    dream_job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True)
    recommended_courses = models.JSONField(default=list)

    def __str__(self):
        return f'Preferences of {self.user.username}'

    class Meta:
        verbose_name_plural = 'User preferences'
