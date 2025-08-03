from django.db import models
from .course_exam_model import Exam

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_number = models.CharField(max_length=10)
    question_text = models.TextField()
    marks = models.FloatField(default=0, null=True, blank=True)

    class Meta:
        unique_together = ('exam', 'question_number')
        ordering = ['question_number']

    def __str__(self):
        return f"Q{self.question_number}: {self.question_text[:50]}"
