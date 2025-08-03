from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class Roles(models.TextChoices):
    ADMIN = 'Admin', _('Admin')
    LECTURER = 'Lecturer', _('Lecturer')
    INVIGILATOR = 'Invigilator', _('Invigilator')
    STUDENT = 'Student', _('Student')
    OFFICIAL = 'Official', _('Official')

class GenderChoices(models.TextChoices):
    MALE = 'Male', _('Male')
    FEMALE = 'Female', _('Female')

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not extra_fields.get('username'):
            raise ValueError('Username is required')
        if not extra_fields.get('first_name') or not extra_fields.get('last_name'):
            raise ValueError('First name and last name are required')
        if not extra_fields.get('gender'):
            raise ValueError('Gender is required for normal users')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # hash password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Roles.ADMIN)
        extra_fields.setdefault('gender', GenderChoices.MALE)
        extra_fields.setdefault('username', 'admin')  
        extra_fields.setdefault('first_name', 'Admin')
        extra_fields.setdefault('last_name', 'User')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    role = models.CharField(max_length=20, choices=Roles.choices)
    device_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # login using email
    REQUIRED_FIELDS = ['username']  # required when using createsuperuser

    def __str__(self):
        return f"{self.email} ({self.role})"
