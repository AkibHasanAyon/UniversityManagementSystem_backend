from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassScheduleViewSet, EnrollmentViewSet, GradeViewSet, AcademicHistoryView, TranscriptView, CourseViewSet, AttendanceViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'schedules', ClassScheduleViewSet, basename='schedule')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    # path('offerings/', ClassScheduleListView.as_view(), name='schedule-list'), # Replaced by schedules/?semester=current
    path('history/', AcademicHistoryView.as_view(), name='academic-history'),
    path('transcript/', TranscriptView.as_view(), name='transcript'),
    path('', include(router.urls)),
]
