from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Q

from .serializers import (
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    StudentSerializer,
    FacultySerializer,
)
from .models import Student, Faculty
from .permissions import IsAdminUser

User = get_user_model()


# ─── Auth Views ────────────────────────────────────────────────────────────

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        reset_link = f"http://localhost:3000/reset-password?uid={uid}&token={token}"

        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_link}',
            'admin@university.edu',
            [email],
            fail_silently=False,
        )

        return Response({'message': 'Password reset link sent to email.'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)


# ─── Pagination ────────────────────────────────────────────────────────────

class StandardPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


# ─── Student Management Views (Admin Only) ─────────────────────────────────

class StudentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/users/students/?search=&page=&page_size=5
    POST /api/users/students/
    """
    serializer_class = StudentSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Student.objects.select_related('user').all()
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(student_id__icontains=search)
            )
        return queryset.order_by('student_id')


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/users/students/{student_id}/
    PUT    /api/users/students/{student_id}/
    DELETE /api/users/students/{student_id}/
    """
    serializer_class = StudentSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'student_id'

    def get_queryset(self):
        return Student.objects.select_related('user').all()

    def perform_destroy(self, instance):
        # Delete both Student profile and associated User
        user = instance.user
        instance.delete()
        user.delete()


# ─── Faculty Management Views (Admin Only) ─────────────────────────────────

class FacultyListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/users/faculty/?search=&page=&page_size=5
    POST /api/users/faculty/
    """
    serializer_class = FacultySerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Faculty.objects.select_related('user').all()
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(department__icontains=search) |
                Q(faculty_id__icontains=search)
            )
        return queryset.order_by('faculty_id')


class FacultyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/users/faculty/{faculty_id}/
    PUT    /api/users/faculty/{faculty_id}/
    DELETE /api/users/faculty/{faculty_id}/
    """
    serializer_class = FacultySerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'faculty_id'

    def get_queryset(self):
        return Faculty.objects.select_related('user').all()

    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        user.delete()
