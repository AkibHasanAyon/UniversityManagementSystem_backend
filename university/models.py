from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Semester(models.Model):
    name = models.CharField(max_length=50) # e.g. Spring 2024
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Classroom(models.Model):
    room_number = models.CharField(max_length=20)
    building = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.building} - {self.room_number}"
