from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from exams.models import Exam
from exams.ocr_utils import extract_questions_from_pdf 



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_question_extraction(request):
    exam_id = request.data.get('exam_id')

    if not exam_id:
        return Response({"error": "Missing exam_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        extract_questions_from_pdf(exam)
        return Response({"success": "Questions extracted successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
