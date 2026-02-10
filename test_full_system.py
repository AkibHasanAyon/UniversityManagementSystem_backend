import os
import django
from datetime import date, time
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import User, Student, Faculty
from university.models import Department, Semester, Classroom
from academic.models import Course, ClassSchedule, Enrollment, Grade
from academic.views import TranscriptView

def test_full_flow():
    print("--- Testing Full System Flow ---")
    
    # 1. Admin Setup
    print("\n1. Admin Setup (Dept, Sem, Room)")
    dept, _ = Department.objects.get_or_create(code="CSE", defaults={'name': 'Computer Science'})
    sem, _ = Semester.objects.get_or_create(name="Fall 2024", defaults={'start_date': date(2024, 9, 1), 'end_date': date(2024, 12, 31), 'is_active': True})
    room, _ = Classroom.objects.get_or_create(room_number="101", building="Main", defaults={'capacity': 50})
    print(f"Created: {dept.name}, {sem.name}, {room}")

    # 2. User Creation
    print("\n2. Creating Users")
    try:
        u_stud = User.objects.create_user("student_final", "st_final@uni.edu", "pass", role="student")
        student = Student.objects.create(user=u_stud, student_id="ST-FINAL", department=dept, year="1st", date_of_birth=date(2005,1,1))
    except:
        u_stud = User.objects.get(email="st_final@uni.edu")
        student = Student.objects.get(student_id="ST-FINAL")

    try:
        u_fac = User.objects.create_user("fac_final", "fac_final@uni.edu", "pass")
    except:
        u_fac = User.objects.get(email="fac_final@uni.edu")
        
    faculty, _ = Faculty.objects.get_or_create(user=u_fac, faculty_id="FAC-FINAL", department=dept, designation="Lecturer", joining_date=date(2020,1,1))
    print(f"Created: Student {student}, Faculty {faculty}")

    # 3. Course & Schedule
    print("\n3. Creating Course & Schedule")
    course, _ = Course.objects.get_or_create(code="CS999", defaults={'name': 'Final Test Course', 'department': dept, 'credits': 3})
    
    # Clean up existing schedules to avoid conflict in test re-runs if needed, or use get_or_create carefully
    # We use a unique time slot
    schedule, created = ClassSchedule.objects.get_or_create(
        course=course, semester=sem, faculty=faculty, classroom=room,
        defaults={'days_of_week': ['Fri'], 'start_time': time(8,0), 'end_time': time(11,0)}
    )
    print(f"Schedule: {schedule}")

    # 4. Enrollment
    print("\n4. Student Enrollment")
    enrollment, _ = Enrollment.objects.get_or_create(student=student, schedule=schedule)
    print(f"Enrolled: {enrollment.status}")

    # 5. Grading
    print("\n5. Faculty Grading")
    # Simulate API grade submission which triggers signal
    grade, _ = Grade.objects.update_or_create(
        enrollment=enrollment,
        defaults={'grade': 'A', 'score': 95, 'graded_by': faculty}
    )
    grade.save() # Trigger signal
    print(f"Graded: {grade.grade} (GPA: {grade.gpa})")

    # 6. Verify Academic History/GPA
    enrollment.refresh_from_db()
    print(f"Enrollment Status: {enrollment.status} (Expected: completed)")
    
    
    # Check Student Current GPA
    student.refresh_from_db()
    print(f"Student Cumulative GPA: {student.current_gpa} (Expected: 4.00)")
    if student.current_gpa != Decimal('4.00'):
         print("CGPA Update Failed")
         return
    
    # 7. Transcript Generation
    print("\n6. Generating Transcript")
    factory = APIRequestFactory()
    view = TranscriptView.as_view()
    request = factory.get('/api/academic/transcript/')
    force_authenticate(request, user=u_stud)
    response = view(request)
    print(f"Transcript Status: {response.status_code}")
    
    if response.status_code == 200:
        print("VERIFICATION SUCCESSFUL")
    else:
        print("VERIFICATION FAILED")

if __name__ == "__main__":
    test_full_flow()
