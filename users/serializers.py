from math import radians, sin, cos, sqrt, asin
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Roles
from django.conf import settings

User = get_user_model()

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees).
    Returns distance in meters.
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371000  # Radius of earth in meters
    return c * r


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.EmailField()  # Change username field to EmailField

    def validate(self, attrs):
        # The default username field is now email
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Extract extra fields from request context
        device_id = self.context['request'].data.get('device_id')
        latitude = self.context['request'].data.get('latitude')
        longitude = self.context['request'].data.get('longitude')

        # Authenticate user
        user = User.objects.filter(email=email).first()
        
        if user is None:
            raise serializers.ValidationError({
                'email': 'No user found with this email address.'
            })
        
        if not user.check_password(password):
            raise serializers.ValidationError({
                'password': 'Incorrect password.'
            })
            
        if not user.is_active:
            raise serializers.ValidationError({
                'email': 'This account is not active.'
            })

        # Only enforce location and device checks for non-students
        if user.role != Roles.STUDENT:
            # Check device_id provided
            if not device_id:
                raise serializers.ValidationError({
                    'device_id': 'Device ID is required for your role.'
                })

            # Validate location provided
            if latitude is None or longitude is None:
                raise serializers.ValidationError({
                    'location': 'Location (latitude and longitude) is required for your role.'
                })

            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except ValueError:
                raise serializers.ValidationError({
                    'location': 'Invalid latitude or longitude values.'
                })

            # Check if location is within campus radius
            distance = haversine(
                longitude, latitude,
                settings.CAMPUS_CENTER['lng'], settings.CAMPUS_CENTER['lat']
            )
            
            if distance > settings.CAMPUS_RADIUS_METERS:
                raise serializers.ValidationError({
                    'location': 'You must be on campus to log in.'
                })

            # Device binding logic
            if user.device_id is None:
                # First login, bind device
                user.device_id = device_id
                user.save(update_fields=['device_id'])
            elif user.device_id != device_id:
                raise serializers.ValidationError({
                    'device_id': 'This device is not authorized for your account.'
                })

        # Generate token
        refresh = self.get_token(user)

        # Prepare response data
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'gender': user.gender,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }

        return data
    


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    new_password = serializers.CharField(write_only=True, required=False)
    verify_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role', 'student_registration_number', 'new_password', 'verify_password')

    def validate(self, data):
        new_password = data.get('new_password')
        verify_password = data.get('verify_password')

        # If either is provided, both must be present and match
        if new_password or verify_password:
            if not new_password:
                raise serializers.ValidationError({"new_password": "This field is required."})
            if not verify_password:
                raise serializers.ValidationError({"verify_password": "This field is required."})
            if new_password != verify_password:
                raise serializers.ValidationError({"verify_password": "Passwords do not match."})
            if len(new_password) < 4:
                raise serializers.ValidationError({"new_password": "Password must be at least 8 characters long."})

        return data

    def update(self, instance, validated_data):
        new_password = validated_data.pop('new_password', None)
        validated_data.pop('verify_password', None)  # Remove it; only used for validation

        # Update fields like first_name, last_name, etc.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If new_password was provided, update password
        if new_password:
            instance.set_password(new_password)

        instance.save()
        return instance




# # serializers.py
# from rest_framework import serializers
# from .models import StudentAnswerPDF

# class StudentAnswerPDFSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentAnswerPDF
#         fields = ['id', 'student_id', 'pdf_file', 'created_at']
