# from rest_framework_simplejwt.views import TokenObtainPairView
# from examsapp.serializers import CustomTokenObtainPairSerializer
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
# from rest_framework import generics, permissions, viewsets
# from examsapp.serializers.user_serializer import StudentRegistrationSerializer
# from examsapp.models import User
# from examsapp.serializers.user_serializer import UserSerializer

# class CustomTokenObtainPairView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer



# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         refresh_token = request.data.get("refresh")
#         if not refresh_token:
#             return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#             return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
#         except (TokenError, InvalidToken):
#             return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)




# # Student registration view
# class StudentRegistrationView(generics.CreateAPIView):
#     serializer_class = StudentRegistrationSerializer
#     permission_classes = [permissions.AllowAny]  # Anyone can register as student


# class UserProfileView(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return User.objects.filter(id=user.id)
