from django.contrib import admin

from .models import User, Instructor, Student, Course

admin.site.register(User)
admin.site.register(Instructor)
admin.site.register(Student)
admin.site.register(Course)
