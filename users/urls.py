from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    StudentListCreateView,
    StudentDetailView,
    FacultyListCreateView,
    FacultyDetailView,
)

urlpatterns = [
    # Auth
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/forgot-password/', PasswordResetRequestView.as_view(), name='forgot_password'),
    path('auth/reset-password/', PasswordResetConfirmView.as_view(), name='reset_password'),

    # Student Management (Admin)
    path('users/students/', StudentListCreateView.as_view(), name='student-list-create'),
    path('users/students/<str:student_id>/', StudentDetailView.as_view(), name='student-detail'),

    # Faculty Management (Admin)
    path('users/faculty/', FacultyListCreateView.as_view(), name='faculty-list-create'),
    path('users/faculty/<str:faculty_id>/', FacultyDetailView.as_view(), name='faculty-detail'),
]
