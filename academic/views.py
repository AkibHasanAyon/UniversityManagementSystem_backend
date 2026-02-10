from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ClassSchedule, Enrollment, Grade, SemesterResult, Course, Attendance
from .serializers import ClassScheduleSerializer, EnrollmentSerializer, GradeSerializer, CourseSerializer, AttendanceSerializer
from university.models import Semester
from users.permissions import IsStudentUser, IsFacultyUser, IsAdminUser

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminUser] # Only Admin creates courses

class ClassScheduleViewSet(viewsets.ModelViewSet):
    queryset = ClassSchedule.objects.all()
    serializer_class = ClassScheduleSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Filter by Active Semester by default, or specific params
        queryset = ClassSchedule.objects.all()
        semester_id = self.request.query_params.get('semester')
        faculty_id = self.request.query_params.get('faculty')
        
        if semester_id:
            if semester_id == 'current':
                active_semester = Semester.objects.filter(is_active=True).first()
                if active_semester:
                    queryset = queryset.filter(semester=active_semester)
            else:
                 queryset = queryset.filter(semester__id=semester_id)
        elif self.action == 'list':
             # Default to active semester for list view unless specified
             active_semester = Semester.objects.filter(is_active=True).first()
             if active_semester:
                queryset = queryset.filter(semester=active_semester)

        if faculty_id:
            queryset = queryset.filter(faculty__id=faculty_id)
            
        return queryset

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsFacultyUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        enrollment_id = self.request.query_params.get('enrollment')
        if enrollment_id:
            return Attendance.objects.filter(enrollment__id=enrollment_id)
        return Attendance.objects.all()

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsStudentUser]

    def get_queryset(self):
        # Return only the requesting student's enrollments
        return Enrollment.objects.filter(student=self.request.user.student_profile)

    def perform_create(self, serializer):
        # The serializer.save() will handle linking student via context
        serializer.save()

    @action(detail=True, methods=['post'])
    def drop(self, request, pk=None):
        enrollment = self.get_object()
        if enrollment.status == 'dropped':
            return Response({'message': 'Already dropped.'}, status=status.HTTP_400_BAD_REQUEST)
        
        enrollment.status = 'dropped'
        enrollment.save()
        return Response({'message': 'Course dropped successfully.'})

class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer
    permission_classes = [IsFacultyUser]

    def get_queryset(self):
        # Faculty sees grades for their schedules
        return Grade.objects.filter(enrollment__schedule__faculty=self.request.user.faculty_profile)

    def perform_create(self, serializer):
        # Check if faculty owns the schedule
        enrollment = serializer.validated_data['enrollment']
        if enrollment.schedule.faculty != self.request.user.faculty_profile:
             raise permissions.PermissionDenied("You can only grade students in your own courses.")
        
        serializer.save(graded_by=self.request.user.faculty_profile)

class AcademicHistoryView(generics.GenericAPIView):
    permission_classes = [IsStudentUser]

    def get(self, request):
        student = request.user.student_profile
        # Fetch completed enrollments with grades
        completed_enrollments = Enrollment.objects.filter(
            student=student, status='completed'
        ).select_related('schedule__course', 'schedule__semester', 'grade')

        history_data = {
            'student_id': student.student_id,
            'name': student.user.get_full_name(),
            'department': str(student.department),
            'total_credits': 0,
            'cgpa': 0.0,
            'semesters': {}
        }

        total_points = 0
        total_graded_credits = 0

        for enrollment in completed_enrollments:
            sem_name = enrollment.schedule.semester.name
            course = enrollment.schedule.course
            grade = getattr(enrollment, 'grade', None)
            
            if sem_name not in history_data['semesters']:
                history_data['semesters'][sem_name] = []

            course_data = {
                'course_code': course.code,
                'course_name': course.name,
                'credits': course.credits,
                'grade': grade.grade if grade else 'N/A',
                'gpa': float(grade.gpa) if grade and grade.gpa else 0.0
            }
            history_data['semesters'][sem_name].append(course_data)
            
            # Calculate stats
            history_data['total_credits'] += course.credits
            if grade and grade.gpa is not None:
                total_points += float(grade.gpa) * course.credits
                total_graded_credits += course.credits

        if total_graded_credits > 0:
            history_data['cgpa'] = round(total_points / total_graded_credits, 2)

        return Response(history_data)

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse

class TranscriptView(generics.GenericAPIView):
    permission_classes = [IsStudentUser]

    def get(self, request):
        student = request.user.student_profile
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="transcript_{student.student_id}.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        y = 750

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y, "University Management System - Official Transcript")
        y -= 30

        # Student Details
        p.setFont("Helvetica", 12)
        p.drawString(50, y, f"Student Name: {student.user.get_full_name()}")
        p.drawString(300, y, f"Student ID: {student.student_id}")
        y -= 20
        p.drawString(50, y, f"Department: {student.department}")
        p.drawString(300, y, f"Date of Birth: {student.date_of_birth}")
        y -= 40

        # Academic Records
        semesters = SemesterResult.objects.filter(student=student).select_related('semester').order_by('semester__start_date')
        
        # Calculate CGPA
        total_gpa_points = 0
        total_credits_earned = 0

        for result in semesters:
            sem = result.semester
            # Draw Semester Header
            if y < 100:
                p.showPage()
                y = 750
            
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, f"Semester: {sem.name} ({sem.start_date.year})")
            p.drawString(400, y, f"SGPA: {result.gpa}")
            y -= 20
            
            # Draw Table Header
            p.setFont("Helvetica-Bold", 10)
            p.drawString(50, y, "Course Code")
            p.drawString(150, y, "Course Name")
            p.drawString(350, y, "Credits")
            p.drawString(450, y, "Grade")
            y -= 15
            p.line(50, y+5, 550, y+5) # Underline
            y -= 5

            # List Courses
            enrollments = Enrollment.objects.filter(
                student=student, schedule__semester=sem, status='completed'
            ).select_related('schedule__course', 'grade')

            p.setFont("Helvetica", 10)
            for e in enrollments:
                if y < 50:
                    p.showPage()
                    y = 750
                
                course = e.schedule.course
                grade = getattr(e, 'grade', None)
                grade_val = grade.grade if grade else "N/A"
                
                p.drawString(50, y, course.code)
                p.drawString(150, y, course.name[:40]) # Truncate long names
                p.drawString(350, y, str(course.credits))
                p.drawString(450, y, grade_val)
                y -= 15
            
            y -= 15 # Spacing between semesters
            
            # Accumulate totals from SemesterResults (can also be done via enrollments)
            # Logic: If using SemesterResult, verify if it aligns with completed enrollments.
            # Assuming SemesterResult.total_credits is correct.
            # However, for CGPA, we need weighted average.
            # Let's rely on the SemesterResults for SGPA display, but calculate CGPA dynamically or use aggregated stats.
            # For simplicity, let's just sum up.
            total_gpa_points += float(result.gpa) * result.total_credits
            total_credits_earned += result.total_credits

        # Footer / Summary
        if y < 100:
            p.showPage()
            y = 750
        
        y -= 20
        p.line(50, y, 550, y)
        y -= 20
        p.setFont("Helvetica-Bold", 12)
        
        cgpa = 0.0
        if total_credits_earned > 0:
            cgpa = round(total_gpa_points / total_credits_earned, 2)
            
        p.drawString(50, y, f"Total Credits Earned: {total_credits_earned}")
        p.drawString(300, y, f"CGPA: {cgpa}")

        p.showPage()
        p.save()
        return response
