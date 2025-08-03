from rest_framework import serializers
from exams.models import Course, Exam,CampusDepartment
from django.contrib.auth import get_user_model

User = get_user_model()

class CourseSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(slug_field='name', queryset=CampusDepartment.objects.all())
    lecturer = serializers.SlugRelatedField(slug_field='first_name', queryset=User.objects.all())
    lecturer_fullname = serializers.SerializerMethodField()

    def get_lecturer_fullname(self, obj):
        return f"{obj.lecturer.first_name} {obj.lecturer.last_name}"
    
    class Meta:
        model = Course
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='code', queryset=Course.objects.all())
    course_name = serializers.SerializerMethodField()
    read_only_fields = ['created_by', 'created', 'updated']

    def get_course_name(self, obj):
        return f"{obj.course.name}"
    
    class Meta:
        model = Exam
        fields = '__all__'