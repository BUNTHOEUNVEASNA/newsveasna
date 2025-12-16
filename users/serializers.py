from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import EmailDigestPreference

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles password confirmation and password validation.
    """
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'is_active')
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'email': {'required': True},
        }

    def validate(self, data):
        """
        Validate matching passwords + password strength.
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })

        # Remove password2 before validating with User()
        temp_data = data.copy()
        temp_data.pop('password2', None)

        # Validate password strength
        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(data['password'], User(**temp_data))
        except ValidationError as e:
            raise serializers.ValidationError({
                "password": list(e.messages)
            })

        return data

    def create(self, validated_data):
        """
        Create new user with hashed password and inactive account (email verification ready).
        """
        validated_data.pop('password2')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False  # for email verification
        )
        return user


class EmailDigestPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for updating email digest preferences.
    """
    class Meta:
        model = EmailDigestPreference
        fields = ('frequency', 'categories', 'is_active')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing/updating user profile + preferences.
    """
    preferences = EmailDigestPreferenceSerializer(
        source='emaildigestpreference',
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'date_joined',
            'preferences'
        )
        read_only_fields = ('id', 'date_joined', 'preferences')
