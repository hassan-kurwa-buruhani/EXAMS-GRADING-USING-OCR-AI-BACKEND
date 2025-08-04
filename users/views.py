from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status, serializers
from .serializers import CustomTokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()
from rest_framework import viewsets, permissions
from .serializers import UserSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    

class UserProfileView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(id=user.id)
    






# views.py
# views.py

# from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.base import ContentFile
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.utils import ImageReader
# from PIL import Image
# from io import BytesIO
# import os

#  # import your model

# class CreateStudentPDF(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request, *args, **kwargs):
#         images = request.FILES.getlist('images')
#         student_id = request.data.get('student_id')

#         if not images:
#             return Response({"error": "No images provided."}, status=status.HTTP_400_BAD_REQUEST)

#         if not student_id:
#             return Response({"error": "student_id is required."}, status=status.HTTP_400_BAD_REQUEST)

#         # Generate PDF
#         pdf_buffer = BytesIO()
#         pdf = canvas.Canvas(pdf_buffer, pagesize=A4)

#         for image_file in images:
#             try:
#                 image = Image.open(image_file)
#                 image_rgb = image.convert("RGB")
#                 img_stream = BytesIO()
#                 image_rgb.save(img_stream, format='PNG')
#                 img_stream.seek(0)

#                 img_reader = ImageReader(img_stream)
#                 pdf.drawImage(img_reader, 0, 0, width=A4[0], height=A4[1], preserveAspectRatio=True)
#                 pdf.showPage()
#             except Exception as e:
#                 return Response({"error": f"Failed to process image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

#         pdf.save()
#         pdf_buffer.seek(0)

#         # Save PDF to model
#         filename = f"student_{student_id}.pdf"
#         django_file = ContentFile(pdf_buffer.read(), name=filename)

#         pdf_record = StudentAnswerPDF.objects.create(
#             student_id=student_id,
#             pdf_file=django_file
#         )

#         return Response({
#             "message": "PDF created and saved to model successfully.",
#             "pdf_id": pdf_record.id,
#             "pdf_url": pdf_record.pdf_file.url
#         }, status=status.HTTP_201_CREATED)
