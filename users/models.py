from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Student(models.Model):
    YEAR_CHOICES = (
        ('1st', 'First Year'),
        ('2nd', 'Second Year'),
        ('3rd', 'Third Year'),
        ('4th', 'Fourth Year'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    major = models.CharField(max_length=100)
    year = models.CharField(max_length=10, choices=YEAR_CHOICES, default='1st')
    current_gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    faculty_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200, blank=True)
    join_date = models.DateField()

    def __str__(self):
        return f"{self.faculty_id} - {self.user.get_full_name()}"
