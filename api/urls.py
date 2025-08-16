from django.urls import path, include
from users.views import CustomTokenObtainPairView, UserProfileView
from django.urls import path, include
from exams.views.course_exam_views import *
from exams.views.question_exam_views import *
from exams.views.student_answer_view import CreateStudentPDF
from exams.views.student_answer_view import GetStudentsAnswerForExam, FetchSTudentAnswerForExam, StudentAnswersListView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from exams.views.ocr_view import trigger_question_extraction
# from users.views import CreateStudentPDF

router = DefaultRouter()
router.register('courses', CourseViewSet, basename='course')
router.register('profile', UserProfileView, basename='profile') 
router.register('exams', ExamViewSet, basename='exam')
router.register(r'exams/(?P<exam_id>[^/.]+)/questions', QuestionPerExamViewSet, 
basename='exam-questions')
router.register(r'exams/(?P<exam_id>[^/.]+)/answers', GetStudentsAnswerForExam, basename='exam-answers')
router.register('exams-invigilator', InvigilatorExamViewSet, basename='exam-invigilator')

router.register(r'exams/(?P<exam_id>\d+)/questions', QuestionPerExamViewsetForAnswerGeneration, basename='questions')

# student view course
router.register('student-course', StudentCourseViewSet, basename='student-courses')

# lecturer view course
router.register('lecturer-course', CoursePerLecturerViewSet, basename='lecturer-course')


# student view exams
router.register('student-exams', StudentExamViewSet, basename='student-exams')
# student view his/her own answer
router.register(r'exams/(?P<exam_id>[^/.]+)/student-answers', FetchSTudentAnswerForExam, basename='student-view-answer')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('questions/', QuestionListView.as_view(), name='questions'),
    # path('answers/', AnswerCreateView.as_view(), name='answers'),

    path('trigger-ocr-question-extraction/', trigger_question_extraction, name='trigger-ocr'),


    path('create-student-pdf/', CreateStudentPDF.as_view(), name='create-student-pdf'),

    path('create-student-answer-pdf/', CreateStudentPDF.as_view(), name='create-student-answer-pdf'),

    # student views his/her own single answer for exam
    path('exams/<int:exam_id>/single-answer/', StudentAnswersListView.as_view(), name='student-single-answer-list'),

]



# from django.urls import path, include
# from examsapp.views.user_views import *
# from examsapp.views.course_exam_views import *
# from examsapp.views.question_exam_views import *
# from rest_framework.routers import DefaultRouter
# from rest_framework_simplejwt.views import TokenRefreshView
# from examsapp.views.ocr_view import trigger_question_extraction

# router = DefaultRouter()
# router.register('courses', CourseViewSet, basename='course')
# router.register('profile', UserProfileView, basename='profile') 
# router.register('exams', ExamViewSet, basename='exam')
# router.register(r'exams/(?P<exam_id>[^/.]+)/questions', QuestionPerExamViewSet, 
# basename='exam-questions')

# router.register(r'exams/(?P<exam_id>\d+)/questions', QuestionPerExamViewsetForAnswerGeneration, basename='questions')


# router.register('lecturer-course', CoursePerLecturerViewSet, basename='lecturer-course')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('logout/', LogoutView.as_view(), name='logout'),

#     path('student-register/', StudentRegistrationView.as_view(), name='student-register'),

#     path('questions/', QuestionListView.as_view(), name='questions'),
#     path('answers/', AnswerCreateView.as_view(), name='answers'),

#     path('trigger-ocr-question-extraction/', trigger_question_extraction, name='trigger-ocr'),
# ]
