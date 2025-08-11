from django.contrib import admin
from django.contrib import admin, messages
from .models import Question, Course, Exam, CollegeCampus, CampusSchool, CampusDepartment, StudentAnswerDocument, StudentAnswer
from .ocr_utils import extract_questions_from_pdf
from .grading_service import grade_answer


# Register your models here.
admin.site.register(Course)
admin.site.register(Question)
admin.site.register(CollegeCampus)
admin.site.register(CampusSchool)
admin.site.register(CampusDepartment)




@admin.register(StudentAnswerDocument)
class StudentAnswerDocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'uploaded_at', 'ocr_extracted')
    actions = ['upload_pdf_to_gcs', 'extract_text_from_selected_pdfs', 'extract_answers_from_notes_admin']

    def upload_pdf_to_gcs(self, request, queryset):
        for obj in queryset:
            try:
                result = obj.upload_to_gcs()
                self.message_user(request, f"✅ {obj} -> {result}")
            except Exception as e:
                self.message_user(request, f"❌ {obj} -> Error: {str(e)}", level='error')
    
    upload_pdf_to_gcs.short_description = "Upload selected PDFs to Google Cloud Storage"


    def extract_text_from_selected_pdfs(self, request, queryset):
        for obj in queryset:
            try:
                result = obj.extract_text_from_pdf()
                self.message_user(request, f"📄 {obj} -> {result}")
            except Exception as e:
                self.message_user(request, f"❌ {obj} -> Error: {str(e)}", level='error')

    extract_text_from_selected_pdfs.short_description = "Extract OCR text from selected PDFs"


    def extract_answers_from_notes_admin(self, request, queryset):
        for obj in queryset:
            try:
                result = obj.extract_answers_from_notes()
                self.message_user(request, f"✏️ {obj} -> {result}")
            except Exception as e:
                self.message_user(request, f"❌ {obj} -> Error: {str(e)}", level='error')


    extract_answers_from_notes_admin.short_description = "Extract answers from OCR notes"


    # def extract_text_from_pdf(self, request, queryset):
    #     for obj in queryset:
    #         try:
    #             result = obj.extract_text_from_pdf()
    #             self.message_user(request, f"✅ {obj} -> {result}")
    #         except Exception as e:
    #             self.message_user(request, f"❌ {obj} -> Error: {str(e)}", level='error')
    
    # extract_text_from_pdf.short_description = "Extract text from selected PDFs"







# @admin.register(StudentAnswer)
# class StudentAnswerAdmin(admin.ModelAdmin):
#     list_display = ('student', 'exam', 'question', 'graded', 'marks_awarded')
#     list_filter = ('exam', 'graded')
#     search_fields = ('student__username', 'question__question_text')
#     actions = ['extract_answers_per_question', 'grade_selected_answers']


#     def grade_selected_answers(self, request, queryset):
#         graded_count = 0
#         for answer in queryset:
#             if answer.graded:
#                 continue  # skip already graded

#             marks, remarks = grade_answer(
#                 question_text=answer.question.question_text,
#                 max_marks=answer.question.marks,
#                 student_answer=answer.answer_text
#             )
#             answer.marks_awarded = marks
#             answer.remarks = remarks
#             answer.graded = True
#             answer.save()
#             graded_count += 1

#         self.message_user(request, f"✅ {graded_count} answers graded.")

#     grade_selected_answers.short_description = "Grade selected answers using AI"




from django.contrib import admin
from .models import StudentAnswer
from .grading_service import grade_answer, grade_student_answers

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'question', 'graded', 'marks_awarded')
    list_filter = ('exam', 'graded')
    search_fields = ('student__username', 'question__question_text')
    actions = ['extract_answers_per_question', 'grade_selected_answers']

    def grade_selected_answers(self, request, queryset):
        graded_count = 0
        # Track which (student, exam) combos need their totals updated
        to_update = set()

        for answer in queryset:
            if answer.graded:
                continue  # skip already graded

            marks, remarks = grade_answer(
                question_text=answer.question.question_text,
                max_marks=answer.question.marks,
                student_answer=answer.answer_text
            )
            answer.marks_awarded = marks
            answer.remarks = remarks
            answer.graded = True
            answer.save()
            graded_count += 1

            # Record for total marks update
            to_update.add((answer.student_id, answer.exam_id))

        # Update totals for each student+exam graded
        for student_id, exam_id in to_update:
            grade_student_answers(student_id, exam_id)

        self.message_user(request, f"✅ {graded_count} answers graded and totals updated.")

    grade_selected_answers.short_description = "Grade selected answers using AI"





    # def extract_answers_per_question(self, request, queryset):
    #     for obj in queryset:
    #         try:
    #             result = obj.extract_answers_to_questions()
    #             self.message_user(request, f"🧾 {obj} -> {result}")
    #         except Exception as e:
    #             self.message_user(request, f"❌ {obj} -> Error: {str(e)}", level='error')

    # extract_answers_per_question.short_description = "Parse OCR text into per-question answers"






@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'date', 'created_by')
    actions = ['extract_questions']

    def extract_questions(self, request, queryset):
        for exam in queryset:
            try:
                extract_questions_from_pdf(exam)
                self.message_user(request, f"Extracted questions for: {exam}", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"Failed to extract for {exam}: {e}", messages.ERROR)

    extract_questions.short_description = "Extract questions from exam PDF"
