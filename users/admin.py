from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Faculty

# Register your models here.
class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student Profile'
    fk_name = 'user'

class FacultyInline(admin.StackedInline):
    model = Faculty
    can_delete = False
    verbose_name_plural = 'Faculty Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (StudentInline, FacultyInline)
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('email',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Faculty)
