import os
import django
from datetime import date, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.exceptions import ValidationError

from university.models import Department, Semester, Classroom
from academic.models import Course, ClassSchedule, Enrollment
from users.models import User, Student, Faculty
from academic.views import EnrollmentViewSet, ClassScheduleListView

def test_enrollment():
    print("--- Testing Enrollment Logic ---")
    
    # Setup Data
    dept, _ = Department.objects.get_or_create(name="CS", code="CS")
    sem, _ = Semester.objects.get_or_create(name="Fall 2024", start_date=date(2024, 9, 1), end_date=date(2024, 12, 31), is_active=True)
    c1, _ = Course.objects.get_or_create(code="CS101", name="Intro to CS", department=dept, credits=3)
    c2, _ = Course.objects.get_or_create(code="CS102", name="Data Structures", department=dept, credits=3)
    classroom, _  = Classroom.objects.get_or_create(room_number="101", building="Main", capacity=50)

    try:
        user_stud = User.objects.create_user(username="student1", email="student1@uni.edu", password="password", role="student")
        student = Student.objects.create(user=user_stud, student_id="STU-001", department=dept, date_of_birth=date(2000, 1, 1))
    except:
        user_stud = User.objects.get(username="student1")
        student = Student.objects.get(student_id="STU-001")

    try:
        user_fac = User.objects.create_user(username="fac1", email="fac1@uni.edu", password="password", role="faculty")
        faculty = Faculty.objects.create(user=user_fac, faculty_id="FAC-001", department=dept, designation="Prof", joining_date=date(2010, 1, 1))
    except:
        faculty = Faculty.objects.get(faculty_id="FAC-001")

    # Create Schedules
    # S1: Mon 10-12
    s1, _ = ClassSchedule.objects.get_or_create(
        course=c1, semester=sem, faculty=faculty, classroom=classroom,
        days_of_week=["Mon"], start_time=time(10, 0), end_time=time(12, 0)
    )
    # S2: Mon 11-13 (Conflicts with S1 time-wise, but different faculty/room to pass Schedule Validation)
    # We need S2 to exist to test ENROLLMENT time conflict for the student.
    
    # Create another faculty/classroom for S2
    try:
        user_fac2 = User.objects.create_user("fac2", "fac2@uni.edu", "pass")
        fac2 = Faculty.objects.create(user=user_fac2, faculty_id="FAC-002", department=dept, designation="L", joining_date=date(2020,1,1))
    except:
        fac2 = Faculty.objects.get(faculty_id="FAC-002")

    classroom2, _ = Classroom.objects.get_or_create(room_number="102", building="Main", capacity=50)

    s2, _ = ClassSchedule.objects.get_or_create(
        course=c2, semester=sem, faculty=fac2, classroom=classroom2,
        days_of_week=["Mon"], start_time=time(11, 0), end_time=time(13, 0)
    )

    print("Setup Complete.")
    
    factory = APIRequestFactory()
    view = EnrollmentViewSet.as_view({'post': 'create'})

    # 1. Enroll in S1
    print("\n1. Enrolling in CS101 (S1)...")
    request = factory.post('/api/academic/enrollments/', {'schedule_id': s1.id})
    force_authenticate(request, user=user_stud)
    response = view(request)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("SUCCESS: Enrolled in S1.")
    else:
        print(f"FAILED: {response.data}")

    # 2. Duplicate Enrollment
    print("\n2. Duplicate Enrollment Check...")
    request = factory.post('/api/academic/enrollments/', {'schedule_id': s1.id})
    force_authenticate(request, user=user_stud)
    response = view(request)
    if response.status_code == 400 and "already enrolled" in str(response.data):
         print("SUCCESS: Duplicate enrollment blocked.")
    else:
         print(f"FAILED: {response.data}")

    # 3. Time Conflict
    print("\n3. Time Conflict Check (Enrolling in CS102 - overlaps S1)...")
    request = factory.post('/api/academic/enrollments/', {'schedule_id': s2.id})
    force_authenticate(request, user=user_stud)
    response = view(request)
    if response.status_code == 400 and "Time conflict" in str(response.data):
        print(f"SUCCESS: Time conflict detected: {response.data}")
    else:
        print(f"FAILED: Conflict ignored! Status: {response.status_code} Data: {response.data}")

    # Cleanup
    Enrollment.objects.filter(student=student).delete()
    s1.delete()
    s2.delete()
    # student.delete()

if __name__ == "__main__":
    test_enrollment()
