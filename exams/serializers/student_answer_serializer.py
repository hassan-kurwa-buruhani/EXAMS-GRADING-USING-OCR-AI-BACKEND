from rest_framework import serializers
from exams.models.student_answer_model import StudentAnswerDocument
from exams.models.course_exam_model import Exam

class StudentAnswerDocumentSerializer(serializers.ModelSerializer):
    exam = serializers.SlugRelatedField(queryset=Exam.objects.all(), slug_field='title')

    class Meta:
        model = StudentAnswerDocument
        fields = '__all__'
        # read_only_fields = ['id', 'uploaded_at', 'ocr_extracted']