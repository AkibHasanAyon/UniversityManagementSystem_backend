import os
import django
from django.core.exceptions import ValidationError
from datetime import date, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from university.models import Department, Semester, Classroom
from academic.models import Course, ClassSchedule
from users.models import User, Faculty

def test_scheduling():
    print("--- Testing Scheduling Logic ---")

    # Setup Data
    dept, _ = Department.objects.get_or_create(name="CS", code="CS101")
    sem, _ = Semester.objects.get_or_create(name="Summer 2024", start_date=date(2024, 5, 1), end_date=date(2024, 8, 30), is_active=True)
    classroom, _ = Classroom.objects.get_or_create(room_number="202", building="Main", capacity=40)
    
    try:
        user = User.objects.create_user(username="prof", email="prof@uni.edu", password="password", role="faculty")
        faculty = Faculty.objects.create(user=user, faculty_id="FAC-002", department=dept, designation="Lecturer", joining_date=date(2020, 1, 1))
    except:
        faculty = Faculty.objects.get(faculty_id="FAC-002")

    print("Setup complete.")

    # 1. Course Credits
    print("\n1. Testing Course Credits...")
    try:
        c = Course(code="CS999", name="Invalid Course", department=dept, credits=10) # Max is 5
        c.full_clean()
        print("FAILED: Invalid credits accepted.")
    except ValidationError as e:
        print(f"SUCCESS: Invalid credits rejected: {e}")

    try:
        c_valid = Course.objects.create(code="CS202", name="Py", department=dept, credits=3)
        print("Valid course created.")
    except:
        c_valid = Course.objects.get(code="CS202")

    # 2. Schedule Conflicts
    print("\n2. Testing Schedule Conflicts...")
    
    # Schedule 1: Mon 10:00 - 12:00
    try:
        s1 = ClassSchedule(
            course=c_valid, semester=sem, faculty=faculty, classroom=classroom,
            days_of_week=["Mon"], start_time=time(10, 0), end_time=time(12, 0)
        )
        s1.save()
        print("Schedule 1 Created (Mon 10-12).")
    except Exception as e:
        print(f"Error creating s1: {e}")

    # Conflict 1: Overlapping Time (Same Faculty)
    try:
        s2 = ClassSchedule(
            course=c_valid, semester=sem, faculty=faculty, classroom=classroom,
            days_of_week=["Mon"], start_time=time(11, 0), end_time=time(13, 0)
        )
        s2.clean() # Manually call clean if not using ModelForm
        print("FAILED: Faculty conflict ignored!")
    except ValidationError as e:
        print(f"SUCCESS: Faculty conflict detected: {e}")

    # Clean up (Optional, but good for re-runs)
    s1.delete()
    # c_valid.delete()
    
if __name__ == "__main__":
    test_scheduling()
