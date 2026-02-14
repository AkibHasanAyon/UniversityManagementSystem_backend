"""
Seed script for University Management System.
Run: python seed_data.py
Creates mock users, courses, assignments, enrollments, and grades.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from users.models import User, Student, Faculty
from academic.models import Course, FacultyCourseAssignment, Enrollment, Grade


def seed():
    print("🌱 Seeding University Management System...")

    # ─── Admin User ────────────────────────────────────────────────
    admin_user, created = User.objects.get_or_create(
        email='admin@university.edu',
        defaults={
            'username': 'admin@university.edu',
            'first_name': 'Dr. Harun Ur',
            'last_name': 'Rashid',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("  ✅ Admin: Dr. Harun Ur Rashid (admin@university.edu / admin123)")
    else:
        print("  ⏭️  Admin already exists")

    # ─── Faculty Users ─────────────────────────────────────────────
    faculty_data = [
        {
            'email': 'rahman@university.edu',
            'first_name': 'Prof.',
            'last_name': 'Rahman',
            'faculty_id': 'FAC001',
            'department': 'Computer Science',
            'specialization': 'Database Systems',
            'join_date': '2020-01-15',
        },
        {
            'email': 'karim@university.edu',
            'first_name': 'Dr.',
            'last_name': 'Karim',
            'faculty_id': 'FAC002',
            'department': 'Mathematics',
            'specialization': 'Linear Algebra',
            'join_date': '2019-06-01',
        },
        {
            'email': 'ahmed@university.edu',
            'first_name': 'Prof.',
            'last_name': 'Ahmed',
            'faculty_id': 'FAC003',
            'department': 'Physics',
            'specialization': 'Quantum Mechanics',
            'join_date': '2021-09-01',
        },
    ]

    faculty_objects = []
    for fd in faculty_data:
        user, created = User.objects.get_or_create(
            email=fd['email'],
            defaults={
                'username': fd['email'],
                'first_name': fd['first_name'],
                'last_name': fd['last_name'],
                'role': 'faculty',
            }
        )
        if created:
            user.set_password('faculty123')
            user.save()

        fac, _ = Faculty.objects.get_or_create(
            faculty_id=fd['faculty_id'],
            defaults={
                'user': user,
                'department': fd['department'],
                'specialization': fd['specialization'],
                'join_date': fd['join_date'],
            }
        )
        faculty_objects.append(fac)
        print(f"  ✅ Faculty: {fd['first_name']} {fd['last_name']} ({fd['faculty_id']})")

    # ─── Student Users ─────────────────────────────────────────────
    student_data = [
        {
            'email': 'ayesha@university.edu',
            'first_name': 'Ayesha',
            'last_name': 'Siddiqua',
            'student_id': 'STU001',
            'major': 'Computer Science',
            'year': '3rd',
            'gpa': '3.75',
        },
        {
            'email': 'rahim@university.edu',
            'first_name': 'Rahim',
            'last_name': 'Uddin',
            'student_id': 'STU002',
            'major': 'Computer Science',
            'year': '2nd',
            'gpa': '3.50',
        },
        {
            'email': 'fatima@university.edu',
            'first_name': 'Fatima',
            'last_name': 'Begum',
            'student_id': 'STU003',
            'major': 'Mathematics',
            'year': '4th',
            'gpa': '3.80',
        },
        {
            'email': 'kamal@university.edu',
            'first_name': 'Kamal',
            'last_name': 'Hasan',
            'student_id': 'STU004',
            'major': 'Physics',
            'year': '1st',
            'gpa': '3.20',
        },
        {
            'email': 'nadia@university.edu',
            'first_name': 'Nadia',
            'last_name': 'Islam',
            'student_id': 'STU005',
            'major': 'Computer Science',
            'year': '3rd',
            'gpa': '3.60',
        },
    ]

    student_objects = []
    for sd in student_data:
        user, created = User.objects.get_or_create(
            email=sd['email'],
            defaults={
                'username': sd['email'],
                'first_name': sd['first_name'],
                'last_name': sd['last_name'],
                'role': 'student',
            }
        )
        if created:
            user.set_password('student123')
            user.save()

        stu, _ = Student.objects.get_or_create(
            student_id=sd['student_id'],
            defaults={
                'user': user,
                'major': sd['major'],
                'year': sd['year'],
                'current_gpa': sd['gpa'],
            }
        )
        student_objects.append(stu)
        print(f"  ✅ Student: {sd['first_name']} {sd['last_name']} ({sd['student_id']})")

    # ─── Courses ───────────────────────────────────────────────────
    course_data = [
        {
            'code': 'CS301',
            'name': 'Database Systems',
            'department': 'Computer Science',
            'credits': 3,
            'semester': 'Fall 2025',
            'days': ['Mon', 'Wed'],
            'start_time': '10:00',
            'end_time': '11:30',
            'room': '301',
            'building': 'Academic Block A',
        },
        {
            'code': 'CS302',
            'name': 'Algorithms',
            'department': 'Computer Science',
            'credits': 3,
            'semester': 'Fall 2025',
            'days': ['Tue', 'Thu'],
            'start_time': '14:00',
            'end_time': '15:30',
            'room': '302',
            'building': 'Academic Block A',
        },
        {
            'code': 'MATH201',
            'name': 'Linear Algebra',
            'department': 'Mathematics',
            'credits': 4,
            'semester': 'Fall 2025',
            'days': ['Mon', 'Wed', 'Fri'],
            'start_time': '09:00',
            'end_time': '10:00',
            'room': '201',
            'building': 'Science Block B',
        },
        {
            'code': 'PHY101',
            'name': 'Physics I',
            'department': 'Physics',
            'credits': 4,
            'semester': 'Fall 2025',
            'days': ['Tue', 'Thu'],
            'start_time': '11:00',
            'end_time': '12:30',
            'room': '101',
            'building': 'Science Block B',
        },
        {
            'code': 'ENG202',
            'name': 'Technical Writing',
            'department': 'English',
            'credits': 3,
            'semester': 'Fall 2025',
            'days': ['Wed', 'Fri'],
            'start_time': '13:00',
            'end_time': '14:30',
            'room': '205',
            'building': 'Arts Block C',
        },
        # Spring 2025 courses (for history)
        {
            'code': 'CS201',
            'name': 'Data Structures',
            'department': 'Computer Science',
            'credits': 3,
            'semester': 'Spring 2025',
            'days': ['Mon', 'Wed'],
            'start_time': '10:00',
            'end_time': '11:30',
            'room': '301',
            'building': 'Academic Block A',
        },
        {
            'code': 'MATH101',
            'name': 'Calculus I',
            'department': 'Mathematics',
            'credits': 4,
            'semester': 'Spring 2025',
            'days': ['Tue', 'Thu'],
            'start_time': '09:00',
            'end_time': '10:30',
            'room': '201',
            'building': 'Science Block B',
        },
    ]

    course_objects = []
    for cd in course_data:
        course, _ = Course.objects.get_or_create(
            code=cd['code'],
            defaults={
                'name': cd['name'],
                'department': cd['department'],
                'credits': cd['credits'],
                'semester': cd['semester'],
                'days': cd['days'],
                'start_time': cd['start_time'],
                'end_time': cd['end_time'],
                'room': cd['room'],
                'building': cd['building'],
            }
        )
        course_objects.append(course)
        print(f"  ✅ Course: {cd['code']} - {cd['name']}")

    # ─── Faculty-Course Assignments ────────────────────────────────
    assignments = [
        ('FAC001', 'CS301'),
        ('FAC001', 'CS302'),
        ('FAC001', 'CS201'),
        ('FAC002', 'MATH201'),
        ('FAC002', 'MATH101'),
        ('FAC003', 'PHY101'),
    ]

    for fac_id, course_code in assignments:
        fac = Faculty.objects.get(faculty_id=fac_id)
        course = Course.objects.get(code=course_code)
        FacultyCourseAssignment.objects.get_or_create(faculty=fac, course=course)
        print(f"  ✅ Assignment: {fac_id} → {course_code}")

    # ─── Enrollments ───────────────────────────────────────────────
    # Current semester enrollments
    enrollments = [
        ('STU001', 'CS301'), ('STU001', 'MATH201'), ('STU001', 'CS302'),
        ('STU001', 'PHY101'), ('STU001', 'ENG202'),
        ('STU002', 'CS301'), ('STU002', 'CS302'), ('STU002', 'MATH201'),
        ('STU003', 'MATH201'), ('STU003', 'PHY101'),
        ('STU004', 'PHY101'), ('STU004', 'ENG202'),
        ('STU005', 'CS301'), ('STU005', 'CS302'),
    ]

    for stu_id, course_code in enrollments:
        student = Student.objects.get(student_id=stu_id)
        course = Course.objects.get(code=course_code)
        Enrollment.objects.get_or_create(student=student, course=course)
        print(f"  ✅ Enrollment: {stu_id} → {course_code}")

    # Past semester enrollments (for history)
    past_enrollments = [
        ('STU001', 'CS201'), ('STU001', 'MATH101'),
        ('STU002', 'CS201'),
        ('STU003', 'MATH101'),
    ]

    for stu_id, course_code in past_enrollments:
        student = Student.objects.get(student_id=stu_id)
        course = Course.objects.get(code=course_code)
        Enrollment.objects.get_or_create(student=student, course=course)
        print(f"  ✅ Past Enrollment: {stu_id} → {course_code}")

    # ─── Grades (for past courses — so history has data) ───────────
    past_grades = [
        ('STU001', 'CS201', 'A', 'FAC001'),
        ('STU001', 'MATH101', 'A-', 'FAC002'),
        ('STU002', 'CS201', 'B+', 'FAC001'),
        ('STU003', 'MATH101', 'A', 'FAC002'),
    ]

    for stu_id, course_code, grade_val, fac_id in past_grades:
        student = Student.objects.get(student_id=stu_id)
        course = Course.objects.get(code=course_code)
        faculty = Faculty.objects.get(faculty_id=fac_id)
        Grade.objects.get_or_create(
            student=student,
            course=course,
            defaults={'grade': grade_val, 'graded_by': faculty}
        )
        print(f"  ✅ Grade: {stu_id} → {course_code} = {grade_val}")

    print("\n🎉 Seeding complete!")
    print("\n📋 Login credentials:")
    print("  Admin:   admin@university.edu / admin123")
    print("  Faculty: rahman@university.edu / faculty123")
    print("  Student: ayesha@university.edu / student123")


if __name__ == '__main__':
    seed()
