import os
import django
import sys

# Set up Django environment
sys.path.append('/home/akib/Desktop/IIT/UniversityManagementSystem_Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from academic.models import FacultyCourseAssignment, Course
from users.models import Faculty

def debug_assignments():
    print("--- Debugging Faculty Assignments ---")
    faculty = Faculty.objects.first() # Get the first faculty (assumed to be Rahman)
    if not faculty:
        print("No faculty found.")
        return
        
    print(f"Faculty: {faculty.user.get_full_name()} ({faculty.faculty_id})")
    
    assignments = FacultyCourseAssignment.objects.filter(faculty=faculty)
    print(f"Total Assignments: {assignments.count()}")
    
    for a in assignments:
        print(f"  - Course ID: {a.course.id}, Code: '{a.course.code}', Name: {a.course.name}")
        
    print("\n--- Testing Specific Course ('MATH101') ---")
    course_code = 'MATH101'
    try:
        course = Course.objects.get(code=course_code)
        print(f"Course Found: ID={course.id}, Code='{course.code}'")
        
        exists = FacultyCourseAssignment.objects.filter(faculty=faculty, course=course).exists()
        print(f"Assignment Exists? {exists}")
    except Course.DoesNotExist:
        print(f"Course with code '{course_code}' does not exist.")
        
    print("\n--- All Courses containing 'MATH' ---")
    math_courses = Course.objects.filter(code__icontains='MATH')
    for c in math_courses:
        print(f"  - ID: {c.id}, Code: '{c.code}'")
        
if __name__ == '__main__':
    debug_assignments()
