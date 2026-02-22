from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


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
        # Email ke string representation hisebe return korchi.
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

    # Student er role define kora hocche.
    def __str__(self):
        # Student ID ebong full name return korbe.
        return f"{self.student_id} - {self.user.get_full_name()}"


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    faculty_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200, blank=True)
    join_date = models.DateField()

    # Faculty er details store korar jonno ei model.
    def __str__(self):
        # Faculty ID ebong full name return korbe.
        return f"{self.faculty_id} - {self.user.get_full_name()}"


class PasswordResetOTP(models.Model):
    """Stores 4-digit OTP for password reset flow."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_otps')
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"OTP for {self.user.email} - {'Used' if self.is_used else 'Active'}"
