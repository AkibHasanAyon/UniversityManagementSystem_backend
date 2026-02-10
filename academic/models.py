from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    department = models.ForeignKey('university.Department', on_delete=models.CASCADE)
    credits = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
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

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if not self.days_of_week:
            raise ValidationError("Days of week cannot be empty.")
            
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
            
        # Check for overlaps
        # SQLite JSON filtering can be tricky. Fetching all schedules for the semester
        # and filtering in Python is safer for this scale.
        schedules = ClassSchedule.objects.filter(
            semester=self.semester
        ).exclude(pk=self.pk)

        # Better Python-side filtering for robust JSON list overlap check
        overlapping_schedules = []
        # Ensure my_days is a set of strings
        if isinstance(self.days_of_week, str):
            import json
            try:
                my_days = set(json.loads(self.days_of_week.replace("'", '"')))
            except:
                my_days = set([self.days_of_week])
        else:
            my_days = set(self.days_of_week)

        for s in schedules:
             # Ensure other_days is a set of strings
            if isinstance(s.days_of_week, str):
                import json
                try:
                    other_days = set(json.loads(s.days_of_week.replace("'", '"')))
                except:
                    other_days = set([s.days_of_week])
            else:
                other_days = set(s.days_of_week)
            
            if my_days.intersection(other_days): # Days overlap
                # Check time overlap
                if self.start_time < s.end_time and self.end_time > s.start_time:
                    overlapping_schedules.append(s)

        for s in overlapping_schedules:
            if s.faculty == self.faculty:
                raise ValidationError(f"Faculty conflict: {self.faculty} is already teaching {s.course} at this time.")
            if s.classroom == self.classroom:
                raise ValidationError(f"Classroom conflict: {self.classroom} is occupied by {s.course}.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        gpa_map = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'F': 0.0
        }
        self.gpa = gpa_map.get(self.grade, 0.0)
        
        # Ensure gpa is saved even if update_fields is specified (e.g. by update_or_create)
        if 'update_fields' in kwargs and kwargs['update_fields']:
            fields = set(kwargs['update_fields'])
            fields.add('gpa')
            kwargs['update_fields'] = list(fields)

        # Mark enrollment as completed
        if self.enrollment.status != 'completed':
            self.enrollment.status = 'completed'
            self.enrollment.save()
            
        super().save(*args, **kwargs)

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

class SemesterResult(models.Model):
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE)
    semester = models.ForeignKey('university.Semester', on_delete=models.CASCADE)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    total_credits = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('student', 'semester')

    def __str__(self):
        return f"{self.student} - {self.semester}: {self.gpa}"

@receiver(post_save, sender=Grade)
def update_semester_gpa(sender, instance, **kwargs):
    enrollment = instance.enrollment
    student = enrollment.student
    semester = enrollment.schedule.semester
    
    # Calculate GPA for this student and semester
    enrollments = Enrollment.objects.filter(
        student=student,
        schedule__semester=semester,
        status='completed',
        grade__isnull=False
    ).select_related('schedule__course', 'grade')
    
    total_points = 0
    total_credits = 0
    
    for e in enrollments:
        credits = e.schedule.course.credits
        if hasattr(e, 'grade') and e.grade.gpa is not None:
            total_points += float(e.grade.gpa) * credits
            total_credits += credits
            
    if total_credits > 0:
        sgpa = round(total_points / total_credits, 2)
    else:
        sgpa = 0.0
        
    SemesterResult.objects.update_or_create(
        student=student,
        semester=semester,
        defaults={'gpa': sgpa, 'total_credits': total_credits}
    )

@receiver(post_save, sender=SemesterResult)
def update_student_cumulative_gpa(sender, instance, **kwargs):
    student = instance.student
    results = SemesterResult.objects.filter(student=student)
    
    total_gpa_points = 0
    total_credits = 0
    
    for res in results:
        total_gpa_points += float(res.gpa) * res.total_credits
        total_credits += res.total_credits
        
    if total_credits > 0:
        cgpa = round(total_gpa_points / total_credits, 2)
    else:
        cgpa = 0.0
        
    student.current_gpa = cgpa
    student.save()
