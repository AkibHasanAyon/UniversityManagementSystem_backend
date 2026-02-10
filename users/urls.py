from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/forgot-password/', PasswordResetRequestView.as_view(), name='forgot_password'),
    path('auth/reset-password/', PasswordResetConfirmView.as_view(), name='reset_password'),
]

from rest_framework.routers import DefaultRouter
from .views import UserViewSet, StudentViewSet, FacultyViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'faculty', FacultyViewSet, basename='faculty')

urlpatterns += router.urls
