from rest_framework import serializers
from .models import Course, FacultyCourseAssignment, Enrollment, Grade
from users.models import Student, Faculty


class CourseSerializer(serializers.ModelSerializer):
    """Flat course+schedule payload matching ManageCourses.jsx form."""

    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name', 'department', 'credits', 'semester',
            'days', 'start_time', 'end_time', 'room', 'building', 'description',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format schedule string for table display: "Mon, Wed 10:00-11:30"
        days_str = ', '.join(instance.days) if instance.days else ''
        time_str = ''
        if instance.start_time and instance.end_time:
            time_str = f"{instance.start_time.strftime('%H:%M')}-{instance.end_time.strftime('%H:%M')}"
        data['schedule'] = f"{days_str} {time_str}".strip() if days_str or time_str else ''
        # Format location string: "Building - Room"
        data['location'] = ''
        if instance.building and instance.room:
            data['location'] = f"{instance.building} - {instance.room}"
        elif instance.building:
            data['location'] = instance.building
        elif instance.room:
            data['location'] = instance.room

        # Include students_count for faculty cards
        data['students_count'] = instance.enrollments.filter(status='Active').count()
        return data


class FacultyCourseAssignmentSerializer(serializers.Serializer):
    """Accepts { faculty_id, course_id } from AssignCourses.jsx."""
    faculty_id = serializers.CharField()
    course_id = serializers.IntegerField(required=False)
    course_code = serializers.CharField(required=False)

    def validate(self, attrs):
        # Resolve faculty
        faculty_id = attrs.get('faculty_id')
        try:
            attrs['faculty_obj'] = Faculty.objects.get(faculty_id=faculty_id)
        except Faculty.DoesNotExist:
            raise serializers.ValidationError(f"Faculty with ID {faculty_id} not found.")

        # Resolve course (by id or code)
        course_id = attrs.get('course_id')
        course_code = attrs.get('course_code')
        if course_id:
            try:
                attrs['course_obj'] = Course.objects.get(pk=course_id)
            except Course.DoesNotExist:
                raise serializers.ValidationError(f"Course with ID {course_id} not found.")
        elif course_code:
            try:
                attrs['course_obj'] = Course.objects.get(code=course_code)
            except Course.DoesNotExist:
                raise serializers.ValidationError(f"Course with code {course_code} not found.")
        else:
            raise serializers.ValidationError("Either course_id or course_code is required.")

        # Duplicate check
        if FacultyCourseAssignment.objects.filter(
            faculty=attrs['faculty_obj'], course=attrs['course_obj']
        ).exists():
            raise serializers.ValidationError("This faculty is already assigned to this course.")

        return attrs

    def create(self, validated_data):
        return FacultyCourseAssignment.objects.create(
            faculty=validated_data['faculty_obj'],
            course=validated_data['course_obj'],
        )

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'faculty_id': instance.faculty.faculty_id,
            'faculty_name': instance.faculty.user.get_full_name(),
            'course_code': instance.course.code,
            'course_name': instance.course.name,
        }


class EnrollmentSerializer(serializers.Serializer):
    """Accepts { student_id, course_code } from StudentEnrollment.jsx."""
    student_id = serializers.CharField()
    course_code = serializers.CharField()

    def validate(self, attrs):
        try:
            attrs['student_obj'] = Student.objects.get(student_id=attrs['student_id'])
        except Student.DoesNotExist:
            raise serializers.ValidationError(f"Student {attrs['student_id']} not found.")

        try:
            attrs['course_obj'] = Course.objects.get(code=attrs['course_code'])
        except Course.DoesNotExist:
            raise serializers.ValidationError(f"Course {attrs['course_code']} not found.")

        # Duplicate check
        if Enrollment.objects.filter(
            student=attrs['student_obj'], course=attrs['course_obj']
        ).exists():
            raise serializers.ValidationError("Student is already enrolled in this course.")

        return attrs

    def create(self, validated_data):
        return Enrollment.objects.create(
            student=validated_data['student_obj'],
            course=validated_data['course_obj'],
        )

    def to_representation(self, instance):
        # Resolve instructor from FacultyCourseAssignment
        assignment = FacultyCourseAssignment.objects.filter(course=instance.course).first()
        instructor = assignment.faculty.user.get_full_name() if assignment else 'Not Assigned'

        return {
            'id': instance.id,
            'studentName': instance.student.user.get_full_name(),
            'studentId': instance.student.student_id,
            'courseCode': instance.course.code,
            'courseName': instance.course.name,
            'semester': instance.course.semester,
            'instructor': instructor,
            'status': instance.status,
            'enrollment_date': instance.enrolled_at.strftime('%Y-%m-%d') if instance.enrolled_at else '',
            # Extra fields for student enrollment view
            'credits': instance.course.credits,
            'schedule': self._format_schedule(instance.course),
            'room': self._format_location(instance.course),
        }

    def _format_schedule(self, course):
        days_str = ', '.join(course.days) if course.days else ''
        time_str = ''
        if course.start_time and course.end_time:
            time_str = f"{course.start_time.strftime('%H:%M')}-{course.end_time.strftime('%H:%M')}"
        return f"{days_str} {time_str}".strip()

    def _format_location(self, course):
        if course.room and course.building:
            return f"{course.room} - {course.building}"
        return course.room or course.building or ''


class BulkGradeSerializer(serializers.Serializer):
    """Accepts { course_code, grades: [{student_id, grade}] } from SubmitGrades.jsx."""
    course_code = serializers.CharField()
    grades = serializers.ListField(child=serializers.DictField())

    def validate(self, attrs):
        try:
            attrs['course_obj'] = Course.objects.get(code=attrs['course_code'])
        except Course.DoesNotExist:
            raise serializers.ValidationError(f"Course {attrs['course_code']} not found.")

        valid_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F']
        for entry in attrs['grades']:
            if 'student_id' not in entry or 'grade' not in entry:
                raise serializers.ValidationError("Each grade entry must have student_id and grade.")
            if entry['grade'] not in valid_grades:
                raise serializers.ValidationError(f"Invalid grade: {entry['grade']}")
            try:
                Student.objects.get(student_id=entry['student_id'])
            except Student.DoesNotExist:
                raise serializers.ValidationError(f"Student {entry['student_id']} not found.")

        return attrs


class GradeSerializer(serializers.ModelSerializer):
    """For reading and updating individual grades."""
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    credits = serializers.IntegerField(source='course.credits', read_only=True)
    semester = serializers.CharField(source='course.semester', read_only=True)
    grade_points = serializers.DecimalField(source='gpa', max_digits=4, decimal_places=2, read_only=True)

    class Meta:
        model = Grade
        fields = [
            'id', 'student_id', 'student_name', 'course_code', 'course_name',
            'grade', 'grade_points', 'credits', 'semester',
        ]
        read_only_fields = ['id', 'student_id', 'student_name', 'course_code',
                            'course_name', 'grade_points', 'credits', 'semester']
