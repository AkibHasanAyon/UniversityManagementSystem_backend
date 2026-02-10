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
        ('1st', 'Wait First Year'),
        ('2nd', 'Second Year'),
        ('3rd', 'Third Year'),
        ('4th', 'Fourth Year'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey('university.Department', on_delete=models.CASCADE)
    major = models.CharField(max_length=100, blank=True)
    year = models.CharField(max_length=10, choices=YEAR_CHOICES, default='1st')
    current_gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=5, blank=True, null=True)

    def current_semester(self):
        # Logic to return current active semester or calculated based on enrollment
        return "Spring 2024" # Placeholder

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    faculty_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey('university.Department', on_delete=models.CASCADE)
    designation = models.CharField(max_length=50)
    specialization = models.CharField(max_length=200, blank=True)
    joining_date = models.DateField()

    def __str__(self):
        return f"{self.faculty_id} - {self.user.get_full_name()}"
