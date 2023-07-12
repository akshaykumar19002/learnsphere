from django.contrib import admin
from django.db import models
from .models import Feedback, Wishlist

admin.site.register(Feedback)
admin.site.register(Wishlist)
