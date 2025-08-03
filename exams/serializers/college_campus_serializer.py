from django.contrib.auth import get_user_model
from rest_framework import serializers
from exams.models import CollegeCampus, CampusSchool, CampusDepartment


User = get_user_model()

class CollegeCampusSerializer(serializers.ModelSerializer):

    class Meta:
        model = CollegeCampus
        fields = '__all__'
        
class CampusSchoolSerializer(serializers.ModelSerializer):
    college_campus = serializers.SlugRelatedField(slug_field='name', queryset=CollegeCampus.objects.all())

    class Meta:
        model = CampusSchool
        fields = '__all__'
        
class CampusDepartmentSerializer(serializers.ModelSerializer):
    campus_school = serializers.SlugRelatedField(slug_field='name', queryset=CampusSchool.objects.all())

    class Meta:
        model = CampusDepartment
        fields = '__all__'

