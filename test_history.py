import os
import django
from datetime import date, time
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from academic.views import AcademicHistoryView
from university.models import Department, Semester, Classroom
from academic.models import Course, ClassSchedule, Enrollment, Grade
from users.models import User, Student, Faculty

def test_history():
    print("--- Testing Academic History Logic ---")
    
    # Setup Data
    dept, _ = Department.objects.get_or_create(code="CS", defaults={'name': 'CS'})
    sem, _ = Semester.objects.get_or_create(name="Spring 2025", defaults={'start_date': date(2025, 1, 1), 'end_date': date(2025, 5, 31), 'is_active': False})
    c1, _ = Course.objects.get_or_create(code="HIST101", defaults={'name': 'Intro', 'department': dept, 'credits': 3})
    c2, _ = Course.objects.get_or_create(code="HIST102", defaults={'name': 'DSA', 'department': dept, 'credits': 4})
    
    try:
        user_stud = User.objects.create_user("student_h", "sh@uni.edu", "pass", role="student")
        student = Student.objects.create(user=user_stud, student_id="ST-H", department=dept, date_of_birth=date(2000,1,1))
    except:
        user_stud = User.objects.get(username="student_h")
        student = Student.objects.get(student_id="ST-H")

    try:
        user_fac = User.objects.create_user("fac_h", "fh@uni.edu", "pass")
    except:
        user_fac = User.objects.get(email="fh@uni.edu")
        
    faculty, _ = Faculty.objects.get_or_create(user=user_fac, faculty_id="FAC-H", department=dept, designation="P", joining_date=date(2010,1,1))

    classroom, _  = Classroom.objects.get_or_create(room_number="101H", building="Main", defaults={'capacity': 50})

    # Enroll & Grade 1 (A = 4.0)
    s1, _ = ClassSchedule.objects.get_or_create(
        course=c1, semester=sem, start_time=time(10,0), end_time=time(12,0),
        defaults={'days_of_week': ['Mon'], 'faculty': faculty, 'classroom': classroom}
    )
    e1, _ = Enrollment.objects.get_or_create(student=student, schedule=s1, defaults={'status': 'completed'})
    e1.status = 'completed' # Ensure completed
    e1.save()
    Grade.objects.update_or_create(enrollment=e1, defaults={'grade': 'A', 'gpa': 4.0})

    # Enroll & Grade 2 (B = 3.0)
    s2, _ = ClassSchedule.objects.get_or_create(
        course=c2, semester=sem, start_time=time(12,0), end_time=time(14,0),
        defaults={'days_of_week': ['Mon'], 'faculty': faculty, 'classroom': classroom}
    )
    e2, _ = Enrollment.objects.get_or_create(student=student, schedule=s2, defaults={'status': 'completed'})
    e2.status = 'completed'
    e2.save()
    Grade.objects.update_or_create(enrollment=e2, defaults={'grade': 'B', 'gpa': 3.0})

    # Expected CGPA: ((3*4.0) + (4*3.0)) / (3+4) = (12 + 12) / 7 = 24 / 7 = 3.43
    
    factory = APIRequestFactory()
    view = AcademicHistoryView.as_view()

    print("\n1. Fetching History...")
    request = factory.get('/api/academic/history/')
    force_authenticate(request, user=user_stud)
    response = view(request)

    if response.status_code == 200:
        data = response.data
        print(f"Total Credits: {data['total_credits']} (Expected 7)")
        print(f"CGPA: {data['cgpa']} (Expected 3.43)")
        
        if data['total_credits'] == 7 and data['cgpa'] == 3.43:
            print("Verification: PASSED")
        else:
            print("Verification: FAILED")
    else:
        print(f"FAILED: {response.data}")

    # Cleanup
    e1.delete()
    e2.delete()
    student.delete()
    user_stud.delete()

if __name__ == "__main__":
    test_history()
