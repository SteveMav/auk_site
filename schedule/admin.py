from django.contrib import admin
from .models import Course, CourseSchedule, Exam, Faculty, Student

# Register your models here.
admin.site.register(Course)
admin.site.register(CourseSchedule)
admin.site.register(Exam)
admin.site.register(Faculty)
admin.site.register(Student)
