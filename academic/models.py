from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    department = models.ForeignKey('university.Department', on_delete=models.CASCADE)
    credits = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class ClassSchedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey('university.Semester', on_delete=models.CASCADE)
    faculty = models.ForeignKey('users.Faculty', on_delete=models.SET_NULL, null=True)
    classroom = models.ForeignKey('university.Classroom', on_delete=models.SET_NULL, null=True)
    days_of_week = models.JSONField(default=list) # e.g. ["Mon", "Wed"]
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'semester', 'faculty'], name='unique_course_schedule')
        ]

    def __str__(self):
        return f"{self.course.code} ({self.semester.name})"

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('enrolled', 'Enrolled'),
        ('dropped', 'Dropped'),
        ('completed', 'Completed'),
    )
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE)
    schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')

    class Meta:
        unique_together = ('student', 'schedule')

    def __str__(self):
        return f"{self.student} - {self.schedule}"

class Grade(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    grade = models.CharField(max_length=5) # A+, B, etc.
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    comments = models.TextField(blank=True)
    graded_by = models.ForeignKey('users.Faculty', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.enrollment} - {self.grade}"

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('enrollment', 'date')
