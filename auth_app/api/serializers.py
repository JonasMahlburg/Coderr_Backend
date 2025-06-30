from rest_framework import serializers
from auth_app.models import UserProfile
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response



class UserProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username', read_only=True, default='')
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, default='')
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, default='')
    email = serializers.EmailField(source='user.email', allow_blank=True, default='')
    type = serializers.CharField(allow_blank=True, default='')
    location = serializers.CharField(allow_blank=True, default='')
    tel = serializers.CharField(allow_blank=True, default='')
    description = serializers.CharField(allow_blank=True, default='')
    working_hours = serializers.CharField(allow_blank=True, default='')
    file = serializers.FileField(allow_empty_file=True, required=False)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'location', 'tel',
            'description', 'working_hours', 'type', 'email', 'created_at', 'file'
        ]
        read_only_fields = ['user', 'username', 'type', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for key, value in representation.items():
            if value is None:
                representation[key] = ''
        return representation
    
    def update(self, instance, validated_data):
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
    username = serializers.CharField(source='user.username', read_only=True, default='')
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, default='')
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, default='')
    file = serializers.FileField(allow_empty_file=True, required=False)
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
    username = serializers.CharField(source='user.username', read_only=True, default='')
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, default='')
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, default='')
    file = serializers.FileField(allow_empty_file=True, required=False)
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

Validates that passwords match and that the email is unique before
creating a new User instance.

Fields:
    id (int): User ID (read-only).
    username (str): Full name of the user (used to construct first and last name).
    email (str): Email address of the user.
    password (str): Password (write-only).
    repeated_password (str): Password confirmation (write-only).
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

        # base_username = username.strip().replace(" ", "").lower()
        # username = base_username
        # counter = 1
        # while User.objects.filter(username=username).exists():
        #     username = f"{base_username}{counter}"
        #     counter += 1

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
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        user = authenticate(self.context.get('request'), username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        attrs['user'] = user
        return attrs
