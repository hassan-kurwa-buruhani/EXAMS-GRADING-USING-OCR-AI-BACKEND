from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
# from .models import StudentAnswerPDF

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'gender', 'role', 'is_staff')
    list_filter = ('role', 'gender', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')

    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'gender', 'username', 'student_registration_number', 'device_id')}),
        ('Roles & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'gender', 'role','student_registration_number', 'password1', 'password2', 'is_staff', 'is_superuser')}
        ),
    )

admin.site.register(User, UserAdmin)
# admin.site.register(StudentAnswerPDF)

