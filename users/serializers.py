from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import get_user_model

from .models import Student, Faculty, PasswordResetOTP

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Returns JWT tokens + user info matching frontend LoginPage expectations."""
    # Login er somy user er details ew pass kora hocche.

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Superuser hole role 'admin' set kora hocche, regardless of DB value.
        role = 'admin' if user.is_superuser else user.role

        # Build the user response with role-specific ID
        user_data = {
            'role': role,
            'name': user.get_full_name() or user.username,
            'email': user.email,
        }

        # User er role check kore specific ID add kora hocche.
        if role == 'student' and hasattr(user, 'student_profile'):
            user_data['id'] = user.student_profile.student_id
        elif role == 'faculty' and hasattr(user, 'faculty_profile'):
            user_data['id'] = user.faculty_profile.faculty_id
        elif role == 'admin':
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


class ForgotPasswordSerializer(serializers.Serializer):
    """Step 1: Validate that the email exists."""
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email address.")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    """Step 2: Validate OTP for the given email."""
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        email = attrs['email']
        otp = attrs['otp']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email address.")

        otp_obj = PasswordResetOTP.objects.filter(
            user=user, otp=otp, is_used=False
        ).order_by('-created_at').first()

        if not otp_obj:
            raise serializers.ValidationError("Invalid OTP code.")

        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP has expired. Please request a new one.")

        attrs['user'] = user
        attrs['otp_obj'] = otp_obj
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """Step 3: Verify OTP again and set new password."""
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4, min_length=4)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        email = attrs['email']
        otp = attrs['otp']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email address.")

        otp_obj = PasswordResetOTP.objects.filter(
            user=user, otp=otp, is_used=False
        ).order_by('-created_at').first()

        if not otp_obj:
            raise serializers.ValidationError("Invalid OTP code.")

        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP has expired. Please request a new one.")

        attrs['user'] = user
        attrs['otp_obj'] = otp_obj
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        otp_obj = self.validated_data['otp_obj']
        user.set_password(self.validated_data['new_password'])
        user.save()
        otp_obj.is_used = True
        otp_obj.save()


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
