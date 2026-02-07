from django.contrib import admin

from .models import Department, Semester, Classroom

# Register your models here.
admin.site.register(Department)
admin.site.register(Semester)
admin.site.register(Classroom)
