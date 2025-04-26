from django.db import models
from django.contrib.auth.models import User

# App: schedule
class Faculty(models.Model):
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=255, null=True, blank=True)
    head_of_faculty = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return self.name

class CPProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return f"CP: {self.user.username} - {self.faculty.name}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='student_images/', blank=True, null=True)
    registration_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

class Course(models.Model):
    name = models.CharField(max_length=255)
    professor = models.CharField(max_length=255)
    total_hours = models.IntegerField(null=True, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class CourseSchedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=[
        ('Lundi', 'Lundi'), ('Mardi', 'Mardi'), ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'), ('Vendredi', 'Vendredi'), ('Samedi', 'Samedi'),
        ('Dimanche', 'Dimanche')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    def __str__(self):
        return f"{self.course.name} - {self.day_of_week} - {self.start_time} - {self.end_time}"

class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=255)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.course.name} - {self.semester} - {self.date} - {self.location}"

class Work(models.Model):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    submitted = models.BooleanField(default=False)
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    def __str__(self):
        return f"{self.title} - {self.course.name} - {self.due_date}"

class CourseFile(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='course_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.course.name} - {self.file.name}"
