import os
import django
from datetime import date, time
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from academic.views import GradeViewSet
from university.models import Department, Semester, Classroom
from academic.models import Course, ClassSchedule, Enrollment, Grade
from users.models import User, Student, Faculty

def test_grading():
    print("--- Testing Grading Logic ---")
    
    # Setup Data
    dept, _ = Department.objects.get_or_create(code="CS", defaults={'name': 'CS'})
    sem, _ = Semester.objects.get_or_create(name="Fall 2024", defaults={'start_date': date(2024, 9, 1), 'end_date': date(2024, 12, 31), 'is_active': True})
    c1, _ = Course.objects.get_or_create(code="CS101", defaults={'name': 'Intro', 'department': dept, 'credits': 3})
    classroom, _  = Classroom.objects.get_or_create(room_number="101", building="Main", defaults={'capacity': 50})

    try:
        user_stud = User.objects.create_user("student_g", "sg@uni.edu", "pass", role="student")
        student = Student.objects.create(user=user_stud, student_id="ST-G", department=dept, date_of_birth=date(2000,1,1))
    except:
        user_stud = User.objects.get(username="student_g")
        student = Student.objects.get(student_id="ST-G")

    try:
        user_fac = User.objects.create_user("fac_g", "fg@uni.edu", "pass", role="faculty")
        faculty = Faculty.objects.create(user=user_fac, faculty_id="FAC-G", department=dept, designation="P", joining_date=date(2010,1,1))
    except:
        user_fac = User.objects.get(username="fac_g")
        faculty = Faculty.objects.get(faculty_id="FAC-G")
    
    # Schedule & Enrollment
    s1, _ = ClassSchedule.objects.get_or_create(
        course=c1, semester=sem, faculty=faculty, classroom=classroom,
        days_of_week=["Mon"], start_time=time(14, 0), end_time=time(16, 0)
    )
    enrollment, _ = Enrollment.objects.get_or_create(student=student, schedule=s1)

    factory = APIRequestFactory()
    view = GradeViewSet.as_view({'post': 'create'})

    # 1. Submit Grade A (GPA 4.0)
    print("\n1. submitting Grade A...")
    data = {'enrollment_id': enrollment.id, 'grade': 'A', 'score': 95, 'comments': 'Great'}
    request = factory.post('/api/academic/grades/', data)
    force_authenticate(request, user=user_fac)
    response = view(request)

    if response.status_code == 201:
        grade_id = response.data['id']
        grade_obj = Grade.objects.get(pk=grade_id)
        print(f"SUCCESS: Grade Created. GPA: {grade_obj.gpa}")
        if grade_obj.gpa == Decimal('4.00'):
            print("GPA Verification: PASSED")
        else:
            print(f"GPA Verification: FAILED (Expected 4.0, got {grade_obj.gpa})")
        
        # Check Enrollment Status
        enrollment.refresh_from_db()
        print(f"Enrollment Status: {enrollment.status}")
        if enrollment.status == 'completed':
            print("Status Verification: PASSED")
        else:
             print("Status Verification: FAILED")
    else:
        print(f"FAILED: {response.data}")

    # Cleanup
    grade_obj.delete()
    enrollment.delete()
    s1.delete()

if __name__ == "__main__":
    test_grading()
