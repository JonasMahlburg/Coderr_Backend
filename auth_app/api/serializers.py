from rest_framework import serializers
from auth_app.models import UserProfile
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response



class UserProfileSerializer(serializers.ModelSerializer):
    """
Serializer for the UserProfile model.

Handles serialization and deserialization of user profile data,
including related user object, biography, and location information.

Fields:
    user (User): Reference to the related user account.
    bio (str): Short biography of the user.
    location (str): Location of the user.
"""
    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'location']


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

        base_username = username.strip().replace(" ", "").lower()
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

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


# class UsernameAuthTokenSerializer(serializers.Serializer):
#     """
#     Serializer for authenticating a user using email and password.

#     Fields:
#         email (str): The user's email address.
#         password (str): The user's password.

#     Methods:
#         validate(attrs): Authenticates the user and returns user object if valid.
#     """
#     username = serializers.CharField(label="Username", write_only=True)
#     password = serializers.CharField(label="Password", style={'input_type': 'password'}, trim_whitespace=False)

#     def validate(self, attrs):
#         """
#         Validate and authenticate the user using provided email and password.

#         Args:
#             attrs (dict): Dictionary containing 'email' and 'password'.

#         Returns:
#             dict: Dictionary including the authenticated user.

#         Raises:
#             serializers.ValidationError: If authentication fails or required fields are missing.
#         """
#         username = attrs.get('username')
#         password = attrs.get('password')

#         if username and password:
#             try:
#                 user = User.objects.get(username=username)
#             except User.DoesNotExist:
#                 raise serializers.ValidationError("Invalid email or password.")

#             user = authenticate(self.context.get('request'), username=user.username, password=password)
#             if not user:
#                 raise serializers.ValidationError("Invalid email or password.")
#         else:
#             raise serializers.ValidationError("Must include 'email' and 'password'.")

#         attrs['user'] = user
#         return attrs
    
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
