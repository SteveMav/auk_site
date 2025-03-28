from django.db import models
from schedule.models import Student

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=50, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

# Create your models here.
