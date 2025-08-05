from django.db import models
from users.models import User, Roles
from .course_exam_model import Exam
from django.core.validators import FileExtensionValidator

class StudentAnswerDocument(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='answers')
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': Roles.STUDENT})
    invigilator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invigilated_answers', limit_choices_to={'role': Roles.INVIGILATOR})
    
    pdf = models.FileField(
        upload_to='student_answers/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    ocr_extracted = models.BooleanField(default=False)  # mark if OCR was already done
    notes = models.TextField(blank=True, null=True)  # Optional

    class Meta:
        unique_together = ('exam', 'student')

    def __str__(self):
        return f"Answer by {self.student.username} for {self.exam.title}"
