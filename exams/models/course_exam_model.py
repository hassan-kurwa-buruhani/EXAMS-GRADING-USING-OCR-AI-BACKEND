from django.db import models
from users.models import User, Roles
from .college_campus_model import CampusSchool, CampusDepartment
from django.core.validators import FileExtensionValidator

class Course(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    department = models.ForeignKey('CampusDepartment', on_delete=models.CASCADE, default=" ")
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': Roles.LECTURER})

    def __str__(self):
        return f"{self.code} - {self.name}"

class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': Roles.LECTURER})

    exam_paper = models.FileField(
        upload_to='exam_papers/', 
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        null=True, blank=True
        )
    
    total_marks = models.FloatField(default=0)
    graded = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"{self.title} ({self.course.code} - {self.course.name})"