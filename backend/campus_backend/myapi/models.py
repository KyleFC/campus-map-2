from django.db import models

class Course(models.Model):
    crn = models.IntegerField(max_digits=5)
    course_code = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    professor = models.CharField(max_length=100)
    fees = models.IntegerField(max_digits=3, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.course_code}) - {self.professor}"

class Session(models.Model):
    course = models.ForeignKey(Course, related_name='sessions', on_delete=models.CASCADE)
    meetday = models.CharField(max_length=10, blank=True, default='')  # Allows blank strings
    start_time = models.CharField(max_length=20, blank=True, default='By Arrangement')
    end_time = models.CharField(max_length=20, blank=True, default='By Arrangement')
    location = models.CharField(max_length=100)

    def __str__(self):
        times = f"from {self.start_time} to {self.end_time}" if self.start_time != 'By Arrangement' else self.start_time
        return f"{self.course.course_code} - {self.location} on {self.meetday} {times}"
