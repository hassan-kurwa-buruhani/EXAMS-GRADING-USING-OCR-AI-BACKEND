from rest_framework import serializers
from exams.models import Course, Exam,CampusDepartment, StudentAnswerDocument
from users.models import User, Roles
from django.contrib.auth import get_user_model

User = get_user_model()

class CourseSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(
        slug_field='name', 
        queryset=CampusDepartment.objects.all()
    )
    lecturer = serializers.SlugRelatedField(
        slug_field='first_name', 
        queryset=User.objects.filter(role=Roles.LECTURER)  # Filter only lecturers
    )
    lecturer_fullname = serializers.SerializerMethodField()
    students = serializers.SlugRelatedField(
        many=True,  # Important for many-to-many relationships
        slug_field='student_registration_number',  # Direct field, no need for student__
        queryset=User.objects.filter(role=Roles.STUDENT),  # Filter only students
        required=False  # Not required for creation
    )

    def get_lecturer_fullname(self, obj):
        return f"{obj.lecturer.first_name} {obj.lecturer.last_name}"
    
    class Meta:
        model = Course
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='code', queryset=Course.objects.all())
    course_name = serializers.SerializerMethodField()
    students_pending_submission = serializers.SerializerMethodField()
    read_only_fields = ['created_by', 'created', 'updated']

    def get_course_name(self, obj):
        return obj.course.name

    def get_students_pending_submission(self, obj):
        # Get all students in the course
        all_students = obj.course.students.all()

        # Get all student IDs that have submitted answers for this exam
        submitted_students_ids = StudentAnswerDocument.objects.filter(exam=obj).values_list('student_id', flat=True)

        # Filter out students who haven't submitted
        pending_students = all_students.exclude(id__in=submitted_students_ids)

        # Return registration numbers
        return [student.student_registration_number for student in pending_students]

    class Meta:
        model = Exam
        fields = '__all__'