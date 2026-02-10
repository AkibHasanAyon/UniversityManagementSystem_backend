from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, SemesterViewSet, ClassroomViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'semesters', SemesterViewSet, basename='semester')
router.register(r'classrooms', ClassroomViewSet, basename='classroom')

urlpatterns = [
    path('', include(router.urls)),
]
