import os
import django
from datetime import date, time
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from academic.views import TranscriptView
from university.models import Department, Semester, Classroom
from academic.models import Course, ClassSchedule, Enrollment, Grade, SemesterResult
from users.models import User, Student, Faculty

def test_gpa_transcript():
    print("--- Testing GPA Auto-Calculation & Transcript ---")
    
    # Setup Data
    dept, _ = Department.objects.get_or_create(code="GPA_TEST", defaults={'name': 'GPA Test Dept'})
    sem, _ = Semester.objects.get_or_create(name="Summer 2025", defaults={'start_date': date(2025, 6, 1), 'end_date': date(2025, 8, 31), 'is_active': True})
    c1, _ = Course.objects.get_or_create(code="GPA101", defaults={'name': 'Course 1', 'department': dept, 'credits': 3})
    c2, _ = Course.objects.get_or_create(code="GPA102", defaults={'name': 'Course 2', 'department': dept, 'credits': 4})
    
    try:
        user_stud = User.objects.create_user("student_gpa", "sgpa@uni.edu", "pass", role="student")
        student = Student.objects.create(user=user_stud, student_id="ST-GPA", department=dept, date_of_birth=date(2000,1,1))
    except:
        user_stud = User.objects.get(email="sgpa@uni.edu")
        student = Student.objects.get(student_id="ST-GPA")

    try:
        user_fac = User.objects.create_user("fac_gpa", "fgpa@uni.edu", "pass")
    except:
        user_fac = User.objects.get(email="fgpa@uni.edu")
        
    faculty, _ = Faculty.objects.get_or_create(user=user_fac, faculty_id="FAC-GPA", department=dept, designation="L", joining_date=date(2010,1,1))
    
    classroom, _  = Classroom.objects.get_or_create(room_number="GPA1", building="Main", defaults={'capacity': 50})

    # Enroll & Grade 1 (A = 4.0)
    s1, _ = ClassSchedule.objects.get_or_create(
        course=c1, semester=sem, start_time=time(8,0), end_time=time(10,0),
        defaults={'days_of_week': ['Tue'], 'faculty': faculty, 'classroom': classroom}
    )
    e1, _ = Enrollment.objects.get_or_create(student=student, schedule=s1, defaults={'status': 'completed'})
    e1.status = 'completed'
    e1.save()
    g1, _ = Grade.objects.update_or_create(enrollment=e1, defaults={'grade': 'A'}) # GPA should be 4.0
    
    # Enroll & Grade 2 (B = 3.0)
    s2, _ = ClassSchedule.objects.get_or_create(
        course=c2, semester=sem, start_time=time(10,0), end_time=time(12,0),
        defaults={'days_of_week': ['Tue'], 'faculty': faculty, 'classroom': classroom}
    )
    e2, _ = Enrollment.objects.get_or_create(student=student, schedule=s2, defaults={'status': 'completed'})
    e2.status = 'completed'
    e2.save()
    g2, _ = Grade.objects.update_or_create(enrollment=e2, defaults={'grade': 'B'}) # GPA should be 3.0
    
    # Check SemesterResult
    # Expected SGPA = ((3*4.0) + (4*3.0)) / 7 = (12+12)/7 = 3.43
    print("\n1. Verifying Auto-calculated SGPA...")
    try:
        result = SemesterResult.objects.get(student=student, semester=sem)
        print(f"SGPA: {result.gpa} (Expected 3.43)")
        if result.gpa == Decimal('3.43'):
            print("GPA Verification: PASSED")
        else:
            print("GPA Verification: FAILED")
    except SemesterResult.DoesNotExist:
        print("GPA Verification: FAILED (SemesterResult not created)")

    # Update Grade 2 to A (4.0)
    print("\n2. Updating Grade and verifying SGPA update...")
    g2.grade = 'A'
    g2.save()
    # Expected SGPA = ((3*4.0) + (4*4.0)) / 7 = 4.0
    result.refresh_from_db()
    print(f"Updated SGPA: {result.gpa} (Expected 4.00)")
    if result.gpa == Decimal('4.00'):
        print("Update Verification: PASSED")
    else:
        print("Update Verification: FAILED")

    # Transcript PDF
    print("\n3. Testing Transcript PDF Generation...")
    factory = APIRequestFactory()
    view = TranscriptView.as_view()
    request = factory.get('/api/academic/transcript/')
    force_authenticate(request, user=user_stud)
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response['Content-Type']}")
    if response.status_code == 200 and response['Content-Type'] == 'application/pdf':
         print("Transcript Verification: PASSED")
    else:
         print("Transcript Verification: FAILED")

    # Cleanup
    # e1.delete(); e2.delete(); student.delete(); user_stud.delete()

if __name__ == "__main__":
    test_gpa_transcript()
