from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Course(models.Model):
    """Combined Course + Schedule model matching frontend ManageCourses form."""
    # Course er details store kora hocche.
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    # Kon department er course sheta indicate kore.
    department = models.CharField(max_length=100)
    credits = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    semester = models.CharField(max_length=50, blank=True)  # e.g. "Fall 2025"
    description = models.TextField(blank=True)

    # Schedule fields (merged from ClassSchedule)
    days = models.JSONField(default=list, blank=True)  # e.g. ["Mon", "Wed"]
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    # Location fields (merged from Classroom)
    room = models.CharField(max_length=50, blank=True)
    building = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class FacultyCourseAssignment(models.Model):
    """Links a faculty member to a course they teach."""
    faculty = models.ForeignKey('users.Faculty', on_delete=models.CASCADE, related_name='assignments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')

    class Meta:
        unique_together = ('faculty', 'course')

    def __str__(self):
        return f"{self.faculty} -> {self.course}"


class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Enrolled', 'Enrolled'),
        ('Dropped', 'Dropped'),
        ('Completed', 'Completed'),
    )
    # Student kon course e enroll ache sheta track kora hocche.
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    # Enrollment er status (Active, Dropped, Completed) manage kora hocche.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} - {self.course}"


class Grade(models.Model):
    GRADE_CHOICES = (
        ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'),
        ('D', 'D'), ('F', 'F'),
    )
    GPA_MAP = {
        'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D': 1.0, 'F': 0.0,
    }

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    graded_by = models.ForeignKey('users.Faculty', on_delete=models.SET_NULL, null=True, related_name='graded')

    class Meta:
        unique_together = ('student', 'course')

    def save(self, *args, **kwargs):
        # Grade save korar somoy GPA automatically calculate kora hocche.
        self.gpa = self.GPA_MAP.get(self.grade, 0.0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.course} - {self.grade}"


@receiver(post_save, sender=Grade)
def update_student_gpa(sender, instance, **kwargs):
    """Recalculate student's cumulative GPA whenever a grade is saved."""
    # Jokhon e kono notun grade add hobe, student er total GPA update hobe.
    student = instance.student
    grades = Grade.objects.filter(student=student).select_related('course')

    total_points = 0
    total_credits = 0

    for g in grades:
        if g.gpa is not None:
            credits = g.course.credits
            total_points += float(g.gpa) * credits
            total_credits += credits

    if total_credits > 0:
        student.current_gpa = round(total_points / total_credits, 2)
    else:
        student.current_gpa = 0.0
    student.save(update_fields=['current_gpa'])
