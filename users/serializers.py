from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import Student, Faculty

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Returns JWT tokens + user info matching frontend LoginPage expectations."""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Build the user response with role-specific ID
        user_data = {
            'role': user.role,
            'name': user.get_full_name() or user.username,
            'email': user.email,
        }

        # Attach the role-specific ID
        if user.role == 'student' and hasattr(user, 'student_profile'):
            user_data['id'] = user.student_profile.student_id
        elif user.role == 'faculty' and hasattr(user, 'faculty_profile'):
            user_data['id'] = user.faculty_profile.faculty_id
        elif user.role == 'admin':
            user_data['id'] = f"ADM{user.pk:03d}"

        data['user'] = user_data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            pass


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Account with this email does not exist.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    uidb64 = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid link")

        if not PasswordResetTokenGenerator().check_token(self.user, attrs['token']):
            raise serializers.ValidationError("Invalid or expired token")

        return attrs

    def save(self, **kwargs):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()
        return self.user


# ─── Student Serializer (flat payload matching ManageStudents.jsx) ─────────

class StudentSerializer(serializers.Serializer):
    """
    Accepts flat payload from frontend:
    { student_id, name, email, password, major, year, gpa }
    Creates/updates both User and Student records.
    """
    student_id = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=False)
    major = serializers.CharField(max_length=100)
    year = serializers.ChoiceField(choices=['1st', '2nd', '3rd', '4th'])
    gpa = serializers.DecimalField(max_digits=4, decimal_places=2)

    def create(self, validated_data):
        name = validated_data['name']
        parts = name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data.get('password', 'changeme123'),
            first_name=first_name,
            last_name=last_name,
            role='student',
        )
        student = Student.objects.create(
            user=user,
            student_id=validated_data['student_id'],
            major=validated_data['major'],
            year=validated_data['year'],
            current_gpa=validated_data['gpa'],
        )
        return student

    def update(self, instance, validated_data):
        name = validated_data.get('name', instance.user.get_full_name())
        parts = name.split(' ', 1)
        instance.user.first_name = parts[0]
        instance.user.last_name = parts[1] if len(parts) > 1 else ''
        instance.user.email = validated_data.get('email', instance.user.email)
        instance.user.username = validated_data.get('email', instance.user.email)
        instance.user.save()

        instance.student_id = validated_data.get('student_id', instance.student_id)
        instance.major = validated_data.get('major', instance.major)
        instance.year = validated_data.get('year', instance.year)
        instance.current_gpa = validated_data.get('gpa', instance.current_gpa)
        instance.save()
        return instance

    def to_representation(self, instance):
        return {
            'student_id': instance.student_id,
            'name': instance.user.get_full_name(),
            'email': instance.user.email,
            'major': instance.major,
            'year': instance.year,
            'gpa': str(instance.current_gpa),
        }


# ─── Faculty Serializer (flat payload matching ManageFaculty.jsx) ──────────

class FacultySerializer(serializers.Serializer):
    """
    Accepts flat payload from frontend:
    { faculty_id, name, email, password, department, specialization, join_date }
    Creates/updates both User and Faculty records.
    """
    faculty_id = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=False)
    department = serializers.CharField(max_length=100)
    specialization = serializers.CharField(max_length=200)
    join_date = serializers.DateField()

    def create(self, validated_data):
        name = validated_data['name']
        parts = name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data.get('password', 'changeme123'),
            first_name=first_name,
            last_name=last_name,
            role='faculty',
        )
        faculty = Faculty.objects.create(
            user=user,
            faculty_id=validated_data['faculty_id'],
            department=validated_data['department'],
            specialization=validated_data['specialization'],
            join_date=validated_data['join_date'],
        )
        return faculty

    def update(self, instance, validated_data):
        name = validated_data.get('name', instance.user.get_full_name())
        parts = name.split(' ', 1)
        instance.user.first_name = parts[0]
        instance.user.last_name = parts[1] if len(parts) > 1 else ''
        instance.user.email = validated_data.get('email', instance.user.email)
        instance.user.username = validated_data.get('email', instance.user.email)
        instance.user.save()

        instance.faculty_id = validated_data.get('faculty_id', instance.faculty_id)
        instance.department = validated_data.get('department', instance.department)
        instance.specialization = validated_data.get('specialization', instance.specialization)
        instance.join_date = validated_data.get('join_date', instance.join_date)
        instance.save()
        return instance

    def to_representation(self, instance):
        return {
            'faculty_id': instance.faculty_id,
            'name': instance.user.get_full_name(),
            'email': instance.user.email,
            'department': instance.department,
            'specialization': instance.specialization,
            'join_date': str(instance.join_date),
        }
