from django.db import models

# Create your models here.
class Course(models.Model):
    course_id = models.CharField(max_length=50, unique=True)
    course_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.CharField(max_length=50)

    def __str__(self):
        return self.course_name

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
