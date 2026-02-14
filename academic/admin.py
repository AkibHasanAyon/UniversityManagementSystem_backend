from django.contrib import admin
from .models import Course, FacultyCourseAssignment, Enrollment, Grade

admin.site.register(Course)
admin.site.register(FacultyCourseAssignment)
admin.site.register(Enrollment)
admin.site.register(Grade)
