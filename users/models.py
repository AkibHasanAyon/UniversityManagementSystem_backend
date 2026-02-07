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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey('university.Department', on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=5, blank=True, null=True)

    def current_semester(self):
        # Placeholder logic
        return "Not calculated"

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    faculty_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey('university.Department', on_delete=models.CASCADE)
    designation = models.CharField(max_length=50)
    joining_date = models.DateField()

    def __str__(self):
        return f"{self.faculty_id} - {self.user.get_full_name()}"
