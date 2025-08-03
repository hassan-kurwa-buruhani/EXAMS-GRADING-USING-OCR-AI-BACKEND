from rest_framework import serializers
from exams.models import Question

class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ['id','question_number', 'question_text', 'marks', 'exam']


