from rest_framework import generics, permissions, viewsets
from exams.models import Question, Exam
from exams.serializers import QuestionSerializer
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


# List all questions
class QuestionListView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


# Create a new answer
# class AnswerCreateView(generics.CreateAPIView):
#     queryset = Answer.objects.all()
#     serializer_class = AnswerSerializer





# questions per exam view(only for lecturers to view the questions of the exams they created)
class QuestionPerExamViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        exam_id = self.kwargs.get('exam_id')

        # Get the exam or return 404 if it doesn't exist
        exam = get_object_or_404(Exam, id=exam_id)

        # Check if the requesting user is the creator (lecturer)
        if exam.created_by != user:
            raise PermissionDenied("You do not have permission to view questions for this exam.")

        # Return only the questions for this exam
        return Question.objects.filter(exam=exam)




# questions per exam view for generating answers 
class QuestionPerExamViewsetForAnswerGeneration(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        exam_id = self.kwargs.get('exam_id')
        exam = get_object_or_404(Exam, id=exam_id)
        if exam.created_by != user:
            raise PermissionDenied("You do not have permission to view questions for this exam.")
        return Question.objects.filter(exam=exam)

