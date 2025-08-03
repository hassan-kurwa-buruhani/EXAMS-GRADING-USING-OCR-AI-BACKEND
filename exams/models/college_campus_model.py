from django.db import models


class CollegeCampus(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    

    def __str__(self):
        return self.name
    

class CampusSchool(models.Model):
    name = models.CharField(max_length=255)
    college_campus = models.ForeignKey(CollegeCampus, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    

class CampusDepartment(models.Model):
    name = models.CharField(max_length=255)
    campus_school = models.ForeignKey(CampusSchool, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name