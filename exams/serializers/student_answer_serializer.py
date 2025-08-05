# serializers.py

from rest_framework import serializers
from exams.models import StudentAnswerDocument, Exam
from users.models import User

class StudentAnswerDocumentSerializer(serializers.ModelSerializer):
    exam = serializers.SlugRelatedField(queryset=Exam.objects.all(), slug_field='title')
    student = serializers.SlugRelatedField(queryset=User.objects.filter(role='Student'), slug_field='student_registration_number')
    invigilator = serializers.SlugRelatedField(
        queryset=User.objects.filter(role='Invigilator'),
        slug_field='username',
        required=False,
    )

    class Meta:
        model = StudentAnswerDocument
        fields = '__all__'
