from django.shortcuts import render
from rest_framework import viewsets
from exams.models import CollegeCampus, CampusSchool, CampusDepartment
from exams.serializers import CollegeCampusSerializer, CampusSchoolSerializer, CampusDepartmentSerializer
from rest_framework.permissions import IsAuthenticated

class CollegeCampusViewSet(viewsets.ModelViewSet):
    queryset = CollegeCampus.objects.all()
    serializer_class = CollegeCampusSerializer
    permission_classes = [IsAuthenticated]

class CampusSchoolViewSet(viewsets.ModelViewSet):
    queryset = CampusSchool.objects.all()
    serializer_class = CampusSchoolSerializer
    permission_classes = [IsAuthenticated]

class CampusDepartmentViewSet(viewsets.ModelViewSet):
    queryset = CampusDepartment.objects.all()
    serializer_class = CampusDepartmentSerializer
    permission_classes = [IsAuthenticated]