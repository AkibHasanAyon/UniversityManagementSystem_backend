from django.urls import path
from .views import (
    CourseListCreateView,
    CourseDetailView,
    AssignmentListCreateView,
    EnrollmentListCreateView,
    EnrollmentDeleteView,
    GradeListView,
    BulkGradeCreateView,
    GradeUpdateView,
    AcademicRecordsView,
    ScheduleTodayView,
    AcademicHistoryView,
    AcademicHistorySummaryView,
    TranscriptView,
)

urlpatterns = [
    # Course Management
    path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),

    # Faculty-Course Assignments
    path('assignments/', AssignmentListCreateView.as_view(), name='assignment-list-create'),

    # Enrollment
    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment-list-create'),
    path('enrollments/<int:pk>/', EnrollmentDeleteView.as_view(), name='enrollment-delete'),

    # Grading
    path('grades/', GradeListView.as_view(), name='grade-list'),
    path('grades/bulk/', BulkGradeCreateView.as_view(), name='grade-bulk-create'),
    path('grades/<int:pk>/', GradeUpdateView.as_view(), name='grade-update'),

    # Academic Records (Admin)
    path('records/', AcademicRecordsView.as_view(), name='academic-records'),

    # Schedule Widget
    path('schedules/today/', ScheduleTodayView.as_view(), name='schedule-today'),

    # Academic History (Student)
    path('history/', AcademicHistoryView.as_view(), name='academic-history'),
    path('history/summary/', AcademicHistorySummaryView.as_view(), name='academic-history-summary'),

    # Transcript (Student)
    path('transcript/', TranscriptView.as_view(), name='transcript'),
]
