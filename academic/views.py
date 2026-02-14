import datetime
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.db.models import Q, Sum
from django.http import HttpResponse

from .models import Course, FacultyCourseAssignment, Enrollment, Grade
from .serializers import (
    CourseSerializer,
    FacultyCourseAssignmentSerializer,
    EnrollmentSerializer,
    BulkGradeSerializer,
    GradeSerializer,
)
from users.models import Student, Faculty
from users.permissions import IsAdminUser, IsFacultyUser, IsStudentUser


# ─── Pagination ────────────────────────────────────────────────────────────

class SmallPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargePagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 100


# ═══════════════════════════════════════════════════════════════════════════
# COURSE MANAGEMENT (Admin CRUD)
# ═══════════════════════════════════════════════════════════════════════════

class CourseListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/academic/courses/?search=&page=&page_size=5&faculty=current
    POST /api/academic/courses/
    """
    serializer_class = CourseSerializer
    pagination_class = SmallPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Course.objects.all()
        search = self.request.query_params.get('search', '').strip()
        faculty_param = self.request.query_params.get('faculty', '').strip()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(department__icontains=search)
            )

        # Faculty: only show their assigned courses
        if faculty_param == 'current' and hasattr(self.request.user, 'faculty_profile'):
            assigned_course_ids = FacultyCourseAssignment.objects.filter(
                faculty=self.request.user.faculty_profile
            ).values_list('course_id', flat=True)
            queryset = queryset.filter(id__in=assigned_course_ids)

        return queryset.order_by('code')


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/academic/courses/{id}/
    PUT    /api/academic/courses/{id}/
    DELETE /api/academic/courses/{id}/
    """
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


# ═══════════════════════════════════════════════════════════════════════════
# FACULTY-COURSE ASSIGNMENT (Admin)
# ═══════════════════════════════════════════════════════════════════════════

class AssignmentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/academic/assignments/
    POST /api/academic/assignments/
    """
    serializer_class = FacultyCourseAssignmentSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return FacultyCourseAssignment.objects.select_related(
            'faculty__user', 'course'
        ).all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ═══════════════════════════════════════════════════════════════════════════
# ENROLLMENT (Admin manages, Faculty/Student reads)
# ═══════════════════════════════════════════════════════════════════════════

class EnrollmentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/academic/enrollments/?search=&student=current&faculty=current&course=
    POST /api/academic/enrollments/
    """
    serializer_class = EnrollmentSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Enrollment.objects.select_related(
            'student__user', 'course'
        ).all()

        user = self.request.user
        search = self.request.query_params.get('search', '').strip()
        student_param = self.request.query_params.get('student', '').strip()
        faculty_param = self.request.query_params.get('faculty', '').strip()
        course_param = self.request.query_params.get('course', '').strip()
        semester_param = self.request.query_params.get('semester', '').strip()

        # Student: only their own enrollments
        if student_param == 'current' and hasattr(user, 'student_profile'):
            queryset = queryset.filter(student=user.student_profile)
        elif user.role == 'student' and hasattr(user, 'student_profile'):
            queryset = queryset.filter(student=user.student_profile)

        # Faculty: only students in their courses
        if faculty_param == 'current' and hasattr(user, 'faculty_profile'):
            assigned_course_ids = FacultyCourseAssignment.objects.filter(
                faculty=user.faculty_profile
            ).values_list('course_id', flat=True)
            queryset = queryset.filter(course_id__in=assigned_course_ids)

        # Filter by course
        if course_param:
            queryset = queryset.filter(course__code=course_param)

        # Filter by semester
        if semester_param:
            queryset = queryset.filter(course__semester=semester_param)

        # Search
        if search:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search) |
                Q(student__user__last_name__icontains=search) |
                Q(student__student_id__icontains=search) |
                Q(course__code__icontains=search)
            )

        return queryset.order_by('-enrolled_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EnrollmentDeleteView(generics.DestroyAPIView):
    """DELETE /api/academic/enrollments/{id}/"""
    permission_classes = [IsAdminUser]
    queryset = Enrollment.objects.all()


# ═══════════════════════════════════════════════════════════════════════════
# GRADING (Faculty submits/updates, Student reads)
# ═══════════════════════════════════════════════════════════════════════════

class GradeListView(generics.ListAPIView):
    """
    GET /api/academic/grades/?faculty=current&student=current&search=
    """
    serializer_class = GradeSerializer

    def get_queryset(self):
        queryset = Grade.objects.select_related(
            'student__user', 'course', 'graded_by__user'
        ).all()

        user = self.request.user
        search = self.request.query_params.get('search', '').strip()
        faculty_param = self.request.query_params.get('faculty', '').strip()
        student_param = self.request.query_params.get('student', '').strip()

        # Faculty: only grades they submitted
        if faculty_param == 'current' and hasattr(user, 'faculty_profile'):
            queryset = queryset.filter(graded_by=user.faculty_profile)
        elif user.role == 'faculty' and hasattr(user, 'faculty_profile'):
            queryset = queryset.filter(graded_by=user.faculty_profile)

        # Student: only their own grades
        if student_param == 'current' and hasattr(user, 'student_profile'):
            queryset = queryset.filter(student=user.student_profile)
        elif user.role == 'student' and hasattr(user, 'student_profile'):
            queryset = queryset.filter(student=user.student_profile)

        if search:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search) |
                Q(student__user__last_name__icontains=search) |
                Q(student__student_id__icontains=search) |
                Q(course__code__icontains=search)
            )

        return queryset.order_by('course__code', 'student__student_id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BulkGradeCreateView(APIView):
    """POST /api/academic/grades/bulk/ — Faculty bulk-submits grades."""
    permission_classes = [IsFacultyUser]

    def post(self, request):
        serializer = BulkGradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = serializer.validated_data['course_obj']
        faculty = request.user.faculty_profile

        # Verify faculty is assigned to this course
        if not FacultyCourseAssignment.objects.filter(faculty=faculty, course=course).exists():
            return Response(
                {'error': 'You are not assigned to this course.'},
                status=status.HTTP_403_FORBIDDEN
            )

        created_grades = []
        for entry in serializer.validated_data['grades']:
            student = Student.objects.get(student_id=entry['student_id'])

            # Verify student is enrolled
            if not Enrollment.objects.filter(student=student, course=course).exists():
                continue

            grade_obj, _ = Grade.objects.update_or_create(
                student=student,
                course=course,
                defaults={
                    'grade': entry['grade'],
                    'graded_by': faculty,
                }
            )
            created_grades.append(grade_obj)

        return Response(
            {'message': 'Grades submitted successfully!', 'count': len(created_grades)},
            status=status.HTTP_201_CREATED
        )


class GradeUpdateView(generics.UpdateAPIView):
    """PUT /api/academic/grades/{id}/ — Faculty updates a single grade."""
    serializer_class = GradeSerializer
    permission_classes = [IsFacultyUser]

    def get_queryset(self):
        return Grade.objects.filter(graded_by=self.request.user.faculty_profile)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_grade = request.data.get('grade')
        valid_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F']

        if new_grade not in valid_grades:
            return Response(
                {'error': f'Invalid grade: {new_grade}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.grade = new_grade
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ═══════════════════════════════════════════════════════════════════════════
# ACADEMIC RECORDS (Admin read-only view of ALL grades)
# ═══════════════════════════════════════════════════════════════════════════

class AcademicRecordsView(generics.ListAPIView):
    """
    GET /api/academic/records/?search=&semester=&page=&page_size=8
    Admin view of all grade records.
    """
    serializer_class = GradeSerializer
    permission_classes = [IsAdminUser]
    pagination_class = LargePagination

    def get_queryset(self):
        queryset = Grade.objects.select_related(
            'student__user', 'course'
        ).all()

        search = self.request.query_params.get('search', '').strip()
        semester = self.request.query_params.get('semester', '').strip()

        if search:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search) |
                Q(student__user__last_name__icontains=search) |
                Q(student__student_id__icontains=search) |
                Q(course__code__icontains=search)
            )
        if semester:
            queryset = queryset.filter(course__semester=semester)

        return queryset.order_by('student__student_id', 'course__code')


# ═══════════════════════════════════════════════════════════════════════════
# CLASS SCHEDULE WIDGET (Today/Tomorrow)
# ═══════════════════════════════════════════════════════════════════════════

class ScheduleTodayView(APIView):
    """
    GET /api/academic/schedules/today/?role=faculty|student
    Returns today's and tomorrow's class schedules.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = datetime.date.today()
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        today_day = day_names[today.weekday()]
        tomorrow_day = day_names[(today.weekday() + 1) % 7]

        if user.role == 'faculty' and hasattr(user, 'faculty_profile'):
            assigned_course_ids = FacultyCourseAssignment.objects.filter(
                faculty=user.faculty_profile
            ).values_list('course_id', flat=True)
            courses = Course.objects.filter(id__in=assigned_course_ids)
        elif user.role == 'student' and hasattr(user, 'student_profile'):
            enrolled_course_ids = Enrollment.objects.filter(
                student=user.student_profile, status='Active'
            ).values_list('course_id', flat=True)
            courses = Course.objects.filter(id__in=enrolled_course_ids)
        else:
            courses = Course.objects.none()

        def build_schedule(courses_qs, target_day):
            result = []
            for c in courses_qs:
                if target_day in (c.days or []):
                    # Get instructor
                    assignment = FacultyCourseAssignment.objects.filter(course=c).first()
                    instructor = assignment.faculty.user.get_full_name() if assignment else ''

                    result.append({
                        'courseCode': c.code,
                        'courseName': c.name,
                        'startTime': c.start_time.strftime('%H:%M') if c.start_time else '',
                        'endTime': c.end_time.strftime('%H:%M') if c.end_time else '',
                        'days': c.days,
                        'room': c.room,
                        'building': c.building,
                        'type': 'Lecture',
                        'status': 'Scheduled',
                        'instructor': instructor,
                    })
            return sorted(result, key=lambda x: x['startTime'])

        return Response({
            'today': build_schedule(courses, today_day),
            'tomorrow': build_schedule(courses, tomorrow_day),
            'today_day': today_day,
            'tomorrow_day': tomorrow_day,
        })


# ═══════════════════════════════════════════════════════════════════════════
# ACADEMIC HISTORY (Student)
# ═══════════════════════════════════════════════════════════════════════════

class AcademicHistoryView(APIView):
    """
    GET /api/academic/history/?student=current
    Returns semester-by-semester grade breakdown.
    """
    permission_classes = [IsStudentUser]

    def get(self, request):
        student = request.user.student_profile
        grades = Grade.objects.filter(student=student).select_related('course').order_by('course__semester')

        # Group by semester
        semesters = {}
        for g in grades:
            sem = g.course.semester or 'Unknown'
            if sem not in semesters:
                semesters[sem] = []
            semesters[sem].append({
                'code': g.course.code,
                'name': g.course.name,
                'grade': g.grade,
                'credits': g.course.credits,
            })

        # Build response with per-semester GPA
        result = []
        for sem, courses in semesters.items():
            total_points = sum(Grade.GPA_MAP.get(c['grade'], 0) * c['credits'] for c in courses)
            total_credits = sum(c['credits'] for c in courses)
            sem_gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0

            result.append({
                'semester': sem,
                'gpa': sem_gpa,
                'courses': courses,
            })

        # Most recent first
        result.reverse()
        return Response(result)


class AcademicHistorySummaryView(APIView):
    """
    GET /api/academic/history/summary/?student=current
    Returns cumulative academic summary stats.
    """
    permission_classes = [IsStudentUser]

    def get(self, request):
        student = request.user.student_profile
        grades = Grade.objects.filter(student=student).select_related('course')

        total_credits = 0
        total_points = 0
        semesters = set()

        for g in grades:
            credits = g.course.credits
            total_credits += credits
            total_points += float(g.gpa or 0) * credits
            if g.course.semester:
                semesters.add(g.course.semester)

        cgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0

        return Response({
            'cumulative_gpa': cgpa,
            'total_credits': total_credits,
            'semesters_count': len(semesters),
            'courses_completed': grades.count(),
        })


# ═══════════════════════════════════════════════════════════════════════════
# TRANSCRIPT (Student — PDF Download)
# ═══════════════════════════════════════════════════════════════════════════

class TranscriptView(APIView):
    """GET /api/academic/transcript/?student=current&format=pdf"""
    permission_classes = [IsStudentUser]

    def get(self, request):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        student = request.user.student_profile
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="transcript_{student.student_id}.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        y = 750

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y, "University Management System - Official Transcript")
        y -= 30

        p.setFont("Helvetica", 12)
        p.drawString(50, y, f"Student Name: {student.user.get_full_name()}")
        p.drawString(350, y, f"Student ID: {student.student_id}")
        y -= 20
        p.drawString(50, y, f"Major: {student.major}")
        p.drawString(350, y, f"Year: {student.year}")
        y -= 40

        # Get grades grouped by semester
        grades = Grade.objects.filter(student=student).select_related('course').order_by('course__semester')

        semesters = {}
        for g in grades:
            sem = g.course.semester or 'Unknown'
            if sem not in semesters:
                semesters[sem] = []
            semesters[sem].append(g)

        total_gpa_points = 0
        total_credits = 0

        for sem, sem_grades in semesters.items():
            if y < 100:
                p.showPage()
                y = 750

            # Semester header
            sem_credits = sum(g.course.credits for g in sem_grades)
            sem_points = sum(float(g.gpa or 0) * g.course.credits for g in sem_grades)
            sem_gpa = round(sem_points / sem_credits, 2) if sem_credits > 0 else 0.0

            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, f"Semester: {sem}")
            p.drawString(400, y, f"SGPA: {sem_gpa}")
            y -= 20

            p.setFont("Helvetica-Bold", 10)
            p.drawString(50, y, "Course Code")
            p.drawString(150, y, "Course Name")
            p.drawString(380, y, "Credits")
            p.drawString(450, y, "Grade")
            y -= 15
            p.line(50, y + 5, 550, y + 5)
            y -= 5

            p.setFont("Helvetica", 10)
            for g in sem_grades:
                if y < 50:
                    p.showPage()
                    y = 750
                p.drawString(50, y, g.course.code)
                p.drawString(150, y, g.course.name[:40])
                p.drawString(380, y, str(g.course.credits))
                p.drawString(450, y, g.grade)
                y -= 15

            y -= 15
            total_gpa_points += sem_points
            total_credits += sem_credits

        # Footer
        if y < 100:
            p.showPage()
            y = 750

        y -= 20
        p.line(50, y, 550, y)
        y -= 20
        p.setFont("Helvetica-Bold", 12)

        cgpa = round(total_gpa_points / total_credits, 2) if total_credits > 0 else 0.0
        p.drawString(50, y, f"Total Credits: {total_credits}")
        p.drawString(300, y, f"CGPA: {cgpa}")

        p.showPage()
        p.save()
        return response


# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD STATS
# ═══════════════════════════════════════════════════════════════════════════

class AdminDashboardStatsView(APIView):
    """GET /api/dashboard/admin/stats/"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({
            'total_students': Student.objects.count(),
            'total_faculty': Faculty.objects.count(),
            'total_courses': Course.objects.count(),
        })


class FacultyDashboardStatsView(APIView):
    """GET /api/dashboard/faculty/stats/"""
    permission_classes = [IsFacultyUser]

    def get(self, request):
        faculty = request.user.faculty_profile
        assigned_course_ids = FacultyCourseAssignment.objects.filter(
            faculty=faculty
        ).values_list('course_id', flat=True)

        total_students = Enrollment.objects.filter(
            course_id__in=assigned_course_ids, status='Active'
        ).values('student').distinct().count()

        return Response({
            'assigned_courses_count': len(assigned_course_ids),
            'total_students_count': total_students,
        })


class StudentDashboardStatsView(APIView):
    """GET /api/dashboard/student/stats/"""
    permission_classes = [IsStudentUser]

    def get(self, request):
        student = request.user.student_profile
        enrolled_count = Enrollment.objects.filter(
            student=student, status='Active'
        ).count()

        return Response({
            'enrolled_courses_count': enrolled_count,
            'current_gpa': str(student.current_gpa),
        })
