"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/', include('users.urls')),
    path('api/academic/', include('academic.urls')),
]

# Dashboard stats URLs are in academic.urls via /api/academic/ prefix,
# but the frontend expects /api/dashboard/... so we add a redirect:
from academic.views import (
    AdminDashboardStatsView,
    FacultyDashboardStatsView,
    StudentDashboardStatsView,
)

urlpatterns += [
    path('api/dashboard/admin/stats/', AdminDashboardStatsView.as_view(), name='admin-dashboard-stats'),
    path('api/dashboard/faculty/stats/', FacultyDashboardStatsView.as_view(), name='faculty-dashboard-stats'),
    path('api/dashboard/student/stats/', StudentDashboardStatsView.as_view(), name='student-dashboard-stats'),
]
