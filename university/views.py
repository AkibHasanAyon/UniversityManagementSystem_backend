from rest_framework import viewsets
from .models import Department, Semester, Classroom
from .serializers import DepartmentSerializer, SemesterSerializer, ClassroomSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] # Admin for write? Or check perms

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all().order_by('-start_date')
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Admin check should be here or in permission classes
        serializer.save()

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
