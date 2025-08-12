# views.py

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from exams.models import StudentAnswerDocument
from exams.serializers import StudentAnswerDocumentSerializer
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from exams.models import Exam
from users.models import User
from rest_framework import viewsets, permissions
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os

class CreateStudentPDF(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')
        exam_id = request.data.get('exam_id')
        reg_number = request.data.get('student_registration_number')
        invigilator_id = request.data.get('invigilator_id')

        if not images or not exam_id or not reg_number:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            exam = Exam.objects.get(id=exam_id)
            student = User.objects.get(student_registration_number=reg_number, role='Student')
            invigilator = None
            if invigilator_id:
                invigilator = User.objects.get(id=invigilator_id, role='Invigilator')
        except User.DoesNotExist:
            return Response({"error": "Invalid student registration number or invigilator ID."}, status=status.HTTP_400_BAD_REQUEST)
        except Exam.DoesNotExist:
            return Response({"error": "Invalid exam ID."}, status=status.HTTP_400_BAD_REQUEST)

        # ❗ Check if answer already exists
        if StudentAnswerDocument.objects.filter(exam=exam, student=student).exists():
            return Response({
                "error": f"A submission already exists for student {reg_number} for this exam."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate PDF
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=A4)

        for image_file in images:
            try:
                image = Image.open(image_file)
                image_rgb = image.convert("RGB")
                img_stream = BytesIO()
                image_rgb.save(img_stream, format='PNG')
                img_stream.seek(0)

                img_reader = ImageReader(img_stream)
                pdf.drawImage(img_reader, 0, 0, width=A4[0], height=A4[1], preserveAspectRatio=True)
                pdf.showPage()
            except Exception as e:
                return Response({"error": f"Failed to process image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        pdf.save()
        pdf_buffer.seek(0)

        pdf_filename = f"student_{student.student_registration_number}_exam_{exam.id}.pdf"
        save_path = os.path.join('media/student_answers', pdf_filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'wb') as f:
            f.write(pdf_buffer.read())

        relative_path = f"student_answers/{pdf_filename}"
        student_answer = StudentAnswerDocument.objects.create(
            exam=exam,
            student=student,
            invigilator=invigilator,
            pdf=relative_path
        )

        serializer = StudentAnswerDocumentSerializer(student_answer)
        return Response({
            "message": "PDF created and saved successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    


class GetStudentsAnswerForExam(viewsets.ModelViewSet):
    serializer_class = StudentAnswerDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        exam_id = self.kwargs.get('exam_id')

        # Get the exam or return 404 if it doesn't exist
        exam = get_object_or_404(Exam, id=exam_id)

        # Check if the requesting user is the creator (lecturer)
        if exam.created_by != user:
            raise PermissionDenied("You do not have permission to view questions for this exam.")

        # Fetch all answer sheets associated with the exam
        return StudentAnswerDocument.objects.filter(exam=exam)
