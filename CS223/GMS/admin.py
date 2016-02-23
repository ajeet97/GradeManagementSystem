from django.contrib import admin

from .models import *

admin.site.register(User)
admin.site.register(Instructor)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Courses_CSE)
admin.site.register(Courses_ME)
admin.site.register(Courses_EE)
admin.site.register(Grade)
