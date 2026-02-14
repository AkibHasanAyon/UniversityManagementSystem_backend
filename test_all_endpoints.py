"""
Comprehensive test script for all University Management System API endpoints.
Tests every workflow described in the frontend specification.
"""
import requests
import json
import sys

BASE = 'http://localhost:8000/api'

passed = 0
failed = 0
errors = []


def test(name, response, expected_status=200, check=None):
    global passed, failed, errors
    ok = response.status_code == expected_status
    if ok and check:
        try:
            ok = check(response.json())
        except Exception as e:
            ok = False
            errors.append(f"  {name}: Check failed — {e}")
    
    if ok:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        detail = ''
        try:
            detail = response.json()
        except:
            detail = response.text[:200]
        errors.append(f"  ❌ {name}: expected {expected_status}, got {response.status_code} — {detail}")
        print(f"  ❌ {name} (status={response.status_code})")


def login(email, password):
    r = requests.post(f'{BASE}/auth/login/', json={'email': email, 'password': password})
    data = r.json()
    return data.get('access'), data.get('user', {})


def auth(token):
    return {'Authorization': f'Bearer {token}'}


# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("1. AUTHENTICATION")
print("=" * 60)

# Login as Admin
admin_token, admin_user = login('admin@university.edu', 'admin123')
assert admin_token, "Admin login failed!"
test("Admin login returns user data", 
     requests.post(f'{BASE}/auth/login/', json={'email': 'admin@university.edu', 'password': 'admin123'}),
     200, lambda d: d['user']['role'] == 'admin' and 'name' in d['user'])

# Login as Faculty
fac_token, fac_user = login('rahman@university.edu', 'faculty123')
assert fac_token, "Faculty login failed!"
test("Faculty login returns user data",
     requests.post(f'{BASE}/auth/login/', json={'email': 'rahman@university.edu', 'password': 'faculty123'}),
     200, lambda d: d['user']['role'] == 'faculty' and d['user']['id'] == 'FAC001')

# Login as Student
stu_token, stu_user = login('ayesha@university.edu', 'student123')
assert stu_token, "Student login failed!"
test("Student login returns user data",
     requests.post(f'{BASE}/auth/login/', json={'email': 'ayesha@university.edu', 'password': 'student123'}),
     200, lambda d: d['user']['role'] == 'student' and d['user']['id'] == 'STU001')

# Forgot password
test("Forgot password",
     requests.post(f'{BASE}/auth/forgot-password/', json={'email': 'admin@university.edu'}),
     200)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("2. ADMIN — DASHBOARD STATS")
print("=" * 60)

r = requests.get(f'{BASE}/dashboard/admin/stats/', headers=auth(admin_token))
test("Admin dashboard stats", r, 200, 
     lambda d: 'total_students' in d and 'total_faculty' in d and 'total_courses' in d)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("3. ADMIN — MANAGE STUDENTS (CRUD)")
print("=" * 60)

# List students
r = requests.get(f'{BASE}/users/students/', headers=auth(admin_token))
test("List students (paginated)", r, 200, lambda d: 'results' in d and 'count' in d)

# Search students
r = requests.get(f'{BASE}/users/students/?search=Ayesha', headers=auth(admin_token))
test("Search students by name", r, 200, lambda d: d['count'] >= 1)

# Create student
new_student = {
    'student_id': 'STU099',
    'name': 'Test Student',
    'email': 'test99@university.edu',
    'password': 'test123',
    'major': 'Computer Science',
    'year': '2nd',
    'gpa': '3.50'
}
r = requests.post(f'{BASE}/users/students/', json=new_student, headers=auth(admin_token))
test("Create student", r, 201, lambda d: d['student_id'] == 'STU099')

# Get student by ID
r = requests.get(f'{BASE}/users/students/STU099/', headers=auth(admin_token))
test("Get student by student_id", r, 200, lambda d: d['student_id'] == 'STU099')

# Update student
r = requests.put(f'{BASE}/users/students/STU099/', 
                 json={**new_student, 'major': 'Physics', 'name': 'Updated Student'},
                 headers=auth(admin_token))
test("Update student", r, 200, lambda d: d['major'] == 'Physics')

# Delete student
r = requests.delete(f'{BASE}/users/students/STU099/', headers=auth(admin_token))
test("Delete student", r, 204)

# Verify deletion
r = requests.get(f'{BASE}/users/students/STU099/', headers=auth(admin_token))
test("Student deleted (404)", r, 404)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("4. ADMIN — MANAGE FACULTY (CRUD)")
print("=" * 60)

# List faculty
r = requests.get(f'{BASE}/users/faculty/', headers=auth(admin_token))
test("List faculty (paginated)", r, 200, lambda d: 'results' in d and 'count' in d)

# Search faculty
r = requests.get(f'{BASE}/users/faculty/?search=Rahman', headers=auth(admin_token))
test("Search faculty by name", r, 200, lambda d: d['count'] >= 1)

# Create faculty
new_faculty = {
    'faculty_id': 'FAC099',
    'name': 'Test Faculty',
    'email': 'testfac@university.edu',
    'password': 'test123',
    'department': 'Engineering',
    'specialization': 'Control Systems',
    'join_date': '2025-01-15'
}
r = requests.post(f'{BASE}/users/faculty/', json=new_faculty, headers=auth(admin_token))
test("Create faculty", r, 201, lambda d: d['faculty_id'] == 'FAC099')

# Update faculty
r = requests.put(f'{BASE}/users/faculty/FAC099/',
                 json={**new_faculty, 'department': 'EE', 'name': 'Updated Faculty'},
                 headers=auth(admin_token))
test("Update faculty", r, 200, lambda d: d['department'] == 'EE')

# Delete faculty
r = requests.delete(f'{BASE}/users/faculty/FAC099/', headers=auth(admin_token))
test("Delete faculty", r, 204)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("5. ADMIN — MANAGE COURSES (CRUD)")
print("=" * 60)

# List courses
r = requests.get(f'{BASE}/academic/courses/', headers=auth(admin_token))
test("List courses (paginated)", r, 200, lambda d: 'results' in d)

# Search courses
r = requests.get(f'{BASE}/academic/courses/?search=Database', headers=auth(admin_token))
test("Search courses", r, 200, lambda d: d['count'] >= 1)

# Create course
new_course = {
    'code': 'CS999',
    'name': 'Test Course',
    'department': 'Computer Science',
    'credits': 3,
    'semester': 'Fall 2025',
    'days': ['Mon', 'Fri'],
    'start_time': '16:00',
    'end_time': '17:30',
    'room': '501',
    'building': 'Academic Block D'
}
r = requests.post(f'{BASE}/academic/courses/', json=new_course, headers=auth(admin_token))
test("Create course", r, 201, lambda d: d['code'] == 'CS999')
course_id = r.json().get('id')

# Update course
r = requests.put(f'{BASE}/academic/courses/{course_id}/',
                 json={**new_course, 'name': 'Updated Course'},
                 headers=auth(admin_token))
test("Update course", r, 200, lambda d: d['name'] == 'Updated Course')

# Delete course
r = requests.delete(f'{BASE}/academic/courses/{course_id}/', headers=auth(admin_token))
test("Delete course", r, 204)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("6. ADMIN — ASSIGN COURSES TO FACULTY")
print("=" * 60)

# List assignments
r = requests.get(f'{BASE}/academic/assignments/', headers=auth(admin_token))
test("List assignments", r, 200, lambda d: isinstance(d, list) and len(d) > 0)

# Create assignment (ENG202 to FAC001)
r = requests.post(f'{BASE}/academic/assignments/',
                  json={'faculty_id': 'FAC001', 'course_code': 'ENG202'},
                  headers=auth(admin_token))
test("Assign course to faculty", r, 201, lambda d: d['faculty_id'] == 'FAC001')

# Duplicate check
r = requests.post(f'{BASE}/academic/assignments/',
                  json={'faculty_id': 'FAC001', 'course_code': 'CS301'},
                  headers=auth(admin_token))
test("Duplicate assignment rejected", r, 400)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("7. ADMIN — STUDENT ENROLLMENT")
print("=" * 60)

# List enrollments
r = requests.get(f'{BASE}/academic/enrollments/', headers=auth(admin_token))
test("List enrollments", r, 200, lambda d: isinstance(d, list))

# Search enrollments
r = requests.get(f'{BASE}/academic/enrollments/?search=Ayesha', headers=auth(admin_token))
test("Search enrollments", r, 200)

# Duplicate enrollment check
r = requests.post(f'{BASE}/academic/enrollments/',
                  json={'student_id': 'STU001', 'course_code': 'CS301'},
                  headers=auth(admin_token))
test("Duplicate enrollment rejected", r, 400)

# New enrollment
r = requests.post(f'{BASE}/academic/enrollments/',
                  json={'student_id': 'STU004', 'course_code': 'CS301'},
                  headers=auth(admin_token))
test("Enroll student", r, 201, lambda d: d['studentId'] == 'STU004')
new_enrollment_id = r.json().get('id')

# Delete enrollment
r = requests.delete(f'{BASE}/academic/enrollments/{new_enrollment_id}/', headers=auth(admin_token))
test("Remove enrollment", r, 204)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("8. ADMIN — ACADEMIC RECORDS")
print("=" * 60)

r = requests.get(f'{BASE}/academic/records/', headers=auth(admin_token))
test("View academic records (paginated)", r, 200, lambda d: 'results' in d)

r = requests.get(f'{BASE}/academic/records/?semester=Spring 2025', headers=auth(admin_token))
test("Filter records by semester", r, 200)

r = requests.get(f'{BASE}/academic/records/?search=STU001', headers=auth(admin_token))
test("Search records by student ID", r, 200)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("9. FACULTY — DASHBOARD STATS")
print("=" * 60)

r = requests.get(f'{BASE}/dashboard/faculty/stats/', headers=auth(fac_token))
test("Faculty dashboard stats", r, 200,
     lambda d: 'assigned_courses_count' in d and 'total_students_count' in d)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("10. FACULTY — VIEW ASSIGNED COURSES")
print("=" * 60)

r = requests.get(f'{BASE}/academic/courses/?faculty=current', headers=auth(fac_token))
test("Faculty assigned courses", r, 200, lambda d: d['count'] >= 1)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("11. FACULTY — VIEW STUDENTS")
print("=" * 60)

r = requests.get(f'{BASE}/academic/enrollments/?faculty=current', headers=auth(fac_token))
test("Faculty view enrolled students", r, 200, lambda d: isinstance(d, list))

r = requests.get(f'{BASE}/academic/enrollments/?faculty=current&course=CS301', headers=auth(fac_token))
test("Faculty view students by course", r, 200)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("12. FACULTY — SUBMIT GRADES (BULK)")
print("=" * 60)

r = requests.post(f'{BASE}/academic/grades/bulk/', headers=auth(fac_token), json={
    'course_code': 'CS301',
    'grades': [
        {'student_id': 'STU001', 'grade': 'A'},
        {'student_id': 'STU002', 'grade': 'B+'},
        {'student_id': 'STU005', 'grade': 'A-'},
    ]
})
test("Bulk submit grades", r, 201, lambda d: d['count'] == 3)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("13. FACULTY — UPDATE GRADES")
print("=" * 60)

# List grades
r = requests.get(f'{BASE}/academic/grades/?faculty=current', headers=auth(fac_token))
test("Faculty view submitted grades", r, 200, lambda d: isinstance(d, list) and len(d) > 0)
grades = r.json()
grade_id = grades[0]['id'] if grades else None

if grade_id:
    r = requests.put(f'{BASE}/academic/grades/{grade_id}/', headers=auth(fac_token),
                     json={'grade': 'A-'})
    test("Update single grade", r, 200, lambda d: d['grade'] == 'A-')

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("14. STUDENT — DASHBOARD STATS")
print("=" * 60)

r = requests.get(f'{BASE}/dashboard/student/stats/', headers=auth(stu_token))
test("Student dashboard stats", r, 200,
     lambda d: 'enrolled_courses_count' in d and 'current_gpa' in d)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("15. STUDENT — VIEW ENROLLMENT")
print("=" * 60)

r = requests.get(f'{BASE}/academic/enrollments/?student=current', headers=auth(stu_token))
test("Student view enrollments", r, 200, lambda d: isinstance(d, list) and len(d) > 0)

# Check enrollment data has all expected fields
if r.json():
    enrollment = r.json()[0]
    test("Enrollment has instructor field", r, 200,
         lambda d: 'instructor' in d[0])
    test("Enrollment has schedule field", r, 200,
         lambda d: 'schedule' in d[0])

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("16. STUDENT — VIEW GRADES")
print("=" * 60)

r = requests.get(f'{BASE}/academic/grades/?student=current', headers=auth(stu_token))
test("Student view grades", r, 200, lambda d: isinstance(d, list))

# Check grade data shape
if r.json():
    test("Grade has grade_points field", r, 200,
         lambda d: 'grade_points' in d[0])
    test("Grade has credits and semester", r, 200,
         lambda d: 'credits' in d[0] and 'semester' in d[0])

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("17. STUDENT — ACADEMIC HISTORY")
print("=" * 60)

r = requests.get(f'{BASE}/academic/history/', headers=auth(stu_token))
test("Student academic history", r, 200,
     lambda d: isinstance(d, list) and len(d) > 0 and 'semester' in d[0] and 'gpa' in d[0] and 'courses' in d[0])

r = requests.get(f'{BASE}/academic/history/summary/', headers=auth(stu_token))
test("Academic history summary", r, 200,
     lambda d: 'cumulative_gpa' in d and 'total_credits' in d and 'semesters_count' in d and 'courses_completed' in d)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("18. STUDENT — TRANSCRIPT")
print("=" * 60)

r = requests.get(f'{BASE}/academic/transcript/', headers=auth(stu_token))
if r.status_code == 200 and 'application/pdf' in r.headers.get('Content-Type', ''):
    passed += 1
    print("  ✅ Download transcript (PDF)")
else:
    failed += 1
    errors.append(f"  ❌ Download transcript (PDF): expected 200/pdf, got {r.status_code}/{r.headers.get('Content-Type')}")
    print(f"  ❌ Download transcript (PDF) (status={r.status_code})")

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("19. CLASS SCHEDULE WIDGET")
print("=" * 60)

r = requests.get(f'{BASE}/academic/schedules/today/', headers=auth(fac_token))
test("Faculty schedule today", r, 200,
     lambda d: 'today' in d and 'tomorrow' in d)

r = requests.get(f'{BASE}/academic/schedules/today/', headers=auth(stu_token))
test("Student schedule today", r, 200,
     lambda d: 'today' in d and 'tomorrow' in d)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("20. PERMISSION CHECKS")
print("=" * 60)

# Student cannot manage students
r = requests.get(f'{BASE}/users/students/', headers=auth(stu_token))
test("Student cannot list students (403)", r, 403)

# Faculty cannot manage courses
r = requests.post(f'{BASE}/academic/courses/', headers=auth(fac_token),
                  json={'code': 'X', 'name': 'X', 'department': 'X', 'credits': 3, 'semester': 'X'})
test("Faculty cannot create courses (403)", r, 403)

# Student cannot submit grades
r = requests.post(f'{BASE}/academic/grades/bulk/', headers=auth(stu_token),
                  json={'course_code': 'CS301', 'grades': []})
test("Student cannot submit grades (403)", r, 403)

# Faculty cannot manage students
r = requests.post(f'{BASE}/users/students/', headers=auth(fac_token),
                  json=new_student)
test("Faculty cannot create students (403)", r, 403)

# Student cannot access admin records
r = requests.get(f'{BASE}/academic/records/', headers=auth(stu_token))
test("Student cannot view admin records (403)", r, 403)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"\n  Total: {passed + failed}")
print(f"  ✅ Passed: {passed}")
print(f"  ❌ Failed: {failed}")

if errors:
    print("\n  Failures:")
    for e in errors:
        print(f"    {e}")

print()
sys.exit(0 if failed == 0 else 1)
