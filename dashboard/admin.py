from django.contrib import admin
from django.db import models
from .models import Feedback, Wishlist, MyCourses

admin.site.register(Feedback)
admin.site.register(Wishlist)
admin.site.register(MyCourses)
