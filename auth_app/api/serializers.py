"""
Serializers for handling user authentication, registration,
and profile data within the auth_app.
"""
from rest_framework import serializers
from auth_app.models import UserProfile
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for full user profile data including contact details and file uploads.
    """
    username = serializers.CharField(source='user.username', read_only=True, default='')
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, default='')
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, default='')
    email = serializers.EmailField(source='user.email', allow_blank=True, default='')
    type = serializers.CharField(allow_blank=True, default='')
    location = serializers.CharField(allow_blank=True, default='')
    tel = serializers.CharField(allow_blank=True, default='')
    description = serializers.CharField(allow_blank=True, default='')
    working_hours = serializers.CharField(allow_blank=True, default='')
    file = serializers.ImageField(allow_empty_file=True, required=False)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'location', 'tel',
            'description', 'working_hours', 'type', 'email', 'created_at', 'file'
        ]
        read_only_fields = ['user', 'username', 'type', 'created_at']

    def to_representation(self, instance):
        """
        Convert the UserProfile instance into a dictionary for serialization.

        Ensures that all fields with None values are represented as empty strings
        for consistent API responses.

        Args:
            instance (UserProfile): The user profile instance to serialize.

        Returns:
            dict: Serialized representation of the user profile.
        """
        representation = super().to_representation(instance)
        for key, value in representation.items():
            if value is None:
                representation[key] = ''
        return representation
    
    def update(self, instance, validated_data):
        """
        Update the UserProfile instance and related User fields with validated data.

        Handles nested user data update and ensures None values are replaced with empty strings.

        Args:
            instance (UserProfile): The existing profile instance to update.
            validated_data (dict): Dictionary of validated data from the request.

        Returns:
            UserProfile: The updated user profile instance.
        """
        user_data = validated_data.pop('user', {})

        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value if value is not None else '')
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value if value is not None else '')
        instance.save()

        return instance


class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for customer profile data (read-limited public fields).
    """
    username = serializers.CharField(source='user.username', read_only=True, default='')
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, default='')
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, default='')
    file = serializers.ImageField(allow_empty_file=True, required=False)
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)
    type = serializers.CharField(read_only=True, default='customer')

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name',
            'file', 'uploaded_at', 'type'
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for key, value in rep.items():
            if value is None:
                rep[key] = ''
        return rep


class BusinessProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for business profile data including contact and company details.
    """
    username = serializers.CharField(source='user.username', read_only=True, default='')
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, default='')
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, default='')
    file = serializers.ImageField(allow_empty_file=True, required=False)
    location = serializers.CharField(allow_blank=True, default='')
    tel = serializers.CharField(allow_blank=True, default='')
    description = serializers.CharField(allow_blank=True, default='')
    working_hours = serializers.CharField(allow_blank=True, default='')
    type = serializers.CharField(read_only=True, default='business')

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type'
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for key, value in rep.items():
            if value is None:
                rep[key] = ''
        return rep


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates that passwords match and that the email and username are unique before
    creating a new User and associated UserProfile instance.

    Fields:
        id (int): User ID (read-only).
        username (str): Full name of the user (used to construct first and last name).
        email (str): Email address of the user.
        password (str): Password (write-only).
        repeated_password (str): Password confirmation (write-only).
        type (str): User type (either 'customer' or 'business').
    """
    email = serializers.EmailField(required=True)
    repeated_password = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True, allow_blank=False)
    type = serializers.ChoiceField(choices=['customer', 'business'])

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        """
        Creates a new User instance after validating the input data.

        Ensures that the provided passwords match, and that both the email and username are unique.
        Automatically splits the username into first and last name components.

        Args:
            validated_data (dict): The validated user input data.

        Returns:
            User: The newly created user instance.
        """
        pw = validated_data.pop('password')
        repeated_pw = validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')
        username = validated_data.pop('username').title()

        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'Passwords do not match'})

        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError({'error': 'This email is already taken'})
        
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'error': 'This username is already taken'})

        names = username.split()
        first_name = names[0] if len(names) > 0 else ""
        last_name = " ".join(names[1:]) if len(names) > 1 else ""

        account = User(
            email=validated_data['email'],
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        account.set_password(pw)
        account.save()

        UserProfile.objects.create(user=account, type=user_type)

        return account



class UsernameAuthTokenSerializer(serializers.Serializer):
    """
    Serializer for authenticating a user using username and password.
    """
    username = serializers.CharField(label="Username", write_only=True)
    password = serializers.CharField(label="Password", style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        """
        Validates the username and password credentials.

        Ensures both fields are provided and authenticates the user.
        Raises a validation error if authentication fails.

        Args:
            attrs (dict): Incoming data with username and password.

        Returns:
            dict: Validated data including authenticated user instance.
        """
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        user = authenticate(self.context.get('request'), username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        attrs['user'] = user
        return attrs
