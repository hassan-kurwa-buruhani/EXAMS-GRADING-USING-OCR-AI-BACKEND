from rest_framework import viewsets, parsers
from rest_framework import permissions
from exams.models.course_exam_model import Course, Exam
from exams.serializers.course_exam_serializer import CourseSerializer, ExamSerializer


# Course view
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes  = [permissions.IsAuthenticated]


# Exam view
class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)



# invigilator exam view for exams that are not graded
class InvigilatorExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Exam.objects.filter(graded=False)
    

# Courses per lecturer view
class CoursePerLecturerViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Course.objects.filter(lecturer=user)
    
# student view for courses
class StudentCourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Course.objects.filter(students=user)


# student view for exams
class StudentExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Exam.objects.filter(course__students=user)
    

