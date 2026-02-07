from django.contrib import admin

from .models import Course, ClassSchedule, Enrollment, Grade, Attendance

# Register your models here.
admin.site.register(Course)
admin.site.register(ClassSchedule)
admin.site.register(Enrollment)
admin.site.register(Grade)
admin.site.register(Attendance)
