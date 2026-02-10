from rest_framework import serializers
from .models import ClassSchedule, Enrollment, Course, Grade, Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='enrollment.student.user.get_full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'enrollment', 'date', 'status', 'student_name']
from university.models import Semester, Department, Classroom
from users.models import Faculty, Student

class CourseSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'department', 'credits', 'description']

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'name', 'is_active']

class FacultySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    class Meta:
        model = Faculty
        fields = ['id', 'faculty_id', 'name']

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'room_number', 'building']

class ClassScheduleSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    semester = SemesterSerializer(read_only=True)
    faculty = FacultySerializer(read_only=True)
    classroom = ClassroomSerializer(read_only=True)

    class Meta:
        model = ClassSchedule
        fields = ['id', 'course', 'semester', 'faculty', 'classroom', 'days_of_week', 'start_time', 'end_time']

class EnrollmentSerializer(serializers.ModelSerializer):
    schedule = ClassScheduleSerializer(read_only=True)
    schedule_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassSchedule.objects.all(), source='schedule', write_only=True
    )
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'schedule', 'schedule_id', 'enrolled_at', 'status']
        read_only_fields = ['student', 'enrolled_at']

    def validate(self, attrs):
        schedule = attrs.get('schedule')
        request = self.context.get('request')
        student = request.user.student_profile
        
        # 1. Already Enrolled Check
        if Enrollment.objects.filter(student=student, schedule=schedule).exists():
            raise serializers.ValidationError("You are already enrolled in this course.")

        # 2. Check Prerequisites/Completion (Simplified: Check if passed before)
        # Assuming Grade model exists and status='completed' means passed.
        # This requires more complex query if Grade is separate. 
        # For now, check if student has enrollment in same course with status='completed'
        completed_enrollments = Enrollment.objects.filter(
            student=student, 
            schedule__course=schedule.course,
            status='completed'
        )
        if completed_enrollments.exists():
             raise serializers.ValidationError("You have already completed this course.")

        # 3. Time Conflict Check
        # Check against active enrollments in the same semester
        active_enrollments = Enrollment.objects.filter(
            student=student,
            schedule__semester=schedule.semester,
            status='enrolled'
        )
        
        # Re-use logic from ClassSchedule.clean() but check against enrolled schedules
        my_days = set(schedule.days_of_week)
        for enrollment in active_enrollments:
            other_schedule = enrollment.schedule
            other_days = set(other_schedule.days_of_week)
            
            if my_days.intersection(other_days):
                if schedule.start_time < other_schedule.end_time and schedule.end_time > other_schedule.start_time:
                     raise serializers.ValidationError(
                         f"Time conflict with {other_schedule.course.code}: {other_schedule.days_of_week} {other_schedule.start_time}-{other_schedule.end_time}"
                     )

        return attrs

    def create(self, validated_data):
        student = self.context['request'].user.student_profile
        validated_data['student'] = student
        return super().create(validated_data)

class GradeSerializer(serializers.ModelSerializer):
    enrollment_id = serializers.PrimaryKeyRelatedField(
        queryset=Enrollment.objects.all(), source='enrollment', write_only=True
    )
    student_name = serializers.CharField(source='enrollment.student.user.get_full_name', read_only=True)
    course_code = serializers.CharField(source='enrollment.schedule.course.code', read_only=True)

    class Meta:
        model = Grade
        fields = ['id', 'enrollment', 'enrollment_id', 'grade', 'gpa', 'score', 'comments', 'student_name', 'course_code']
        read_only_fields = ['enrollment', 'gpa']
