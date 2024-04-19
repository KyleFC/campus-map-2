from django.db import models

# Create your models here.
class Course(models.Model):
    course_code = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    professor = models.CharField(max_length=100)
    fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

class Session(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    meetday = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100)
    enrolled = models.IntegerField()
    max_capacity = models.IntegerField()