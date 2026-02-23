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
import random


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

    first_names = ["Ali", "Tahmid", "Sadia", "Nusrat", "Farhan", "Mahmud", "Rubel", "Sakib", "Tamim", "Mehedi", "Taskin", "Zakir", "Ebadot", "Suma", "Tariq", "Hasan", "Rina", "Mina", "Tina", "Bina", "Joti", "Rumi", "Sumi", "Lima"]
    last_names = ["Rahman", "Hossain", "Islam", "Uddin", "Ahmed", "Khan", "Chowdhury", "Ali", "Hasan", "Mahmud", "Sikder", "Mirza", "Sheikh", "Talukder", "Molla"]

    for i in range(4, 16):
        faculty_data.append({
            'email': f'faculty{i}@university.edu',
            'first_name': 'Dr.',
            'last_name': f'{random.choice(first_names)} {random.choice(last_names)}',
            'faculty_id': f'FAC{i:03d}',
            'department': random.choice(["Computer Science", "BBA", "EEE"]),
            'specialization': 'General',
            'join_date': f'20{random.randint(10, 24):02d}-01-01',
        })

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

    for i in range(6, 106):
        major = random.choice(["Computer Science", "BBA", "EEE"])
        student_data.append({
            'email': f'student{i}@university.edu',
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'student_id': f'STU{i:03d}',
            'major': major,
            'year': random.choice(["1st", "2nd", "3rd", "4th"]),
            'gpa': f'{random.uniform(2.5, 4.0):.2f}',
        })

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

    cse_courses = [('CS101', 'Intro to CS'), ('CS102', 'Programming Fundamentals'), ('CS202', 'OOP'), ('CS303', 'Operating Systems'), ('CS304', 'Networking'), ('CS401', 'Artificial Intelligence'), ('CS402', 'Machine Learning'), ('CS405', 'Web Development')]
    bba_courses = [('BBA101', 'Intro to Business'), ('BBA102', 'Accounting'), ('BBA201', 'Marketing'), ('BBA202', 'Finance'), ('BBA301', 'HRM'), ('BBA302', 'Business Law'), ('BBA401', 'Strategy')]
    eee_courses = [('EEE101', 'Circuit Theory'), ('EEE102', 'Electronics I'), ('EEE201', 'Signals'), ('EEE202', 'Electromagnetics'), ('EEE301', 'Microprocessors'), ('EEE302', 'Power Systems'), ('EEE401', 'Control Systems')]

    for code, name in cse_courses:
        course_data.append({'code': code, 'name': name, 'department': 'Computer Science', 'credits': 3, 'semester': 'Fall 2025', 'days': ['Mon', 'Wed'], 'start_time': '10:00', 'end_time': '11:30', 'room': '101', 'building': 'Academic Block A'})

    for code, name in bba_courses:
        course_data.append({'code': code, 'name': name, 'department': 'BBA', 'credits': 3, 'semester': 'Fall 2025', 'days': ['Tue', 'Thu'], 'start_time': '12:00', 'end_time': '13:30', 'room': '201', 'building': 'Arts Block C'})

    for code, name in eee_courses:
        course_data.append({'code': code, 'name': name, 'department': 'EEE', 'credits': 3, 'semester': 'Fall 2025', 'days': ['Mon', 'Wed'], 'start_time': '14:00', 'end_time': '15:30', 'room': '301', 'building': 'Science Block B'})

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

    # Randomly assign faculty to other courses based on department
    print("  Assigning remaining courses to faculty...")
    all_faculties = Faculty.objects.all()
    all_courses = Course.objects.all()
    for course in all_courses:
        if not FacultyCourseAssignment.objects.filter(course=course).exists():
            dept_faculties = all_faculties.filter(department=course.department)
            if dept_faculties.exists():
                fac = random.choice(list(dept_faculties))
            else:
                fac = random.choice(list(all_faculties))
            FacultyCourseAssignment.objects.get_or_create(faculty=fac, course=course)
            print(f"  ✅ Random Assignment: {fac.faculty_id} → {course.code}")

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

    print("  Assigning random courses to students...")
    all_students = Student.objects.all()
    all_courses = Course.objects.all()

    for student in all_students:
        if not Enrollment.objects.filter(student=student).exists():
            major_courses = list(all_courses.filter(department=student.major))
            if major_courses:
                num_courses = min(len(major_courses), random.randint(3, 5))
                selected_courses = random.sample(major_courses, num_courses)
                for course in selected_courses:
                    Enrollment.objects.get_or_create(student=student, course=course)
    print("  ✅ Random enrollments assigned successfully!")

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
