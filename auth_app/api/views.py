"""
Views for managing user authentication, registration,
login, and profile data within the auth_app.
"""
from rest_framework import generics, status
from django.contrib.auth.models import User
from auth_app.models import UserProfile
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from .serializers import RegistrationSerializer, UsernameAuthTokenSerializer, UserProfileSerializer, CustomerProfileSerializer, BusinessProfileSerializer
from .permissions import IsOwner, IsAuthenticated


class UserProfileList(generics.ListCreateAPIView):
    """
    API view to list all user profiles or create a new user profile.

    Inherits from Django REST Framework's ListCreateAPIView.
    Uses the RegistrationSerializer to serialize profile data.

    Methods:
        get(): Returns a list of all user profiles.
        post(): Creates a new user profile from request data.
    """
    queryset = UserProfile.objects.all()
    serializer_class = RegistrationSerializer


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific user profile by ID.

    Inherits from RetrieveUpdateDestroyAPIView to provide full CRUD support
    for individual user profiles, including GET, PUT, PATCH, and DELETE.
    Uses the UserProfileSerializer for data serialization and deserialization.

    Methods:
        get(): Retrieves a user profile by ID.
        put(): Fully updates a user profile by ID.
        patch(): Partially updates a user profile by ID.
        delete(): Deletes a user profile by ID.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwner]

    def get_object(self):
        """
        Overrides the default method to retrieve the UserProfile object
        based on the 'pk' (which represents the user's ID in your setup).
        Ensures that object-level permissions are checked.
        """
        user_id = self.kwargs['pk']
        obj = generics.get_object_or_404(UserProfile, user__id=user_id)
        self.check_object_permissions(self.request, obj)
        return obj


class RegistrationView(APIView):
    """
    API view to register a new user and return authentication token.

    Accepts user data, creates a new user upon validation,
    and returns token and user details. Uses the RegistrationSerializer.

    Methods:
        post(): Handles user registration and token creation.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}

        if serializer.is_valid():
            saved_account = serializer.save()
            token, _ = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'username': f"{saved_account.first_name} {saved_account.last_name}".strip(),
                'email': saved_account.email,
                'user_id': saved_account.id,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class CustomLogInView(ObtainAuthToken):
    """
    API view for user login using token authentication.

    Authenticates user based on provided email and password.
    Returns token and user information on success.

    Methods:
        post(): Authenticates and logs in the user.
    """
    permission_classes= [AllowAny]
    serializer_class= UsernameAuthTokenSerializer  

    def post(self, request):
        serializer = self.serializer_class(
            data={
                'username': request.data.get('username'),
                'password': request.data.get('password')
            },
            context={'request': request}
        )

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            username = f"{user.first_name} {user.last_name}".strip()
            data = {
                'token': token.key,
                'username': username,
                'email': user.email,
                'user_id': user.id,
    
            }
            return Response(data)
        else:
            return Response(
                {'error': 'Invalid username or password'},
                status=status.HTTP_400_BAD_REQUEST)
            

class BusinessUserListView(generics.ListAPIView):
    """
    API view to list all users with type 'business'.

    Inherits from ListAPIView and filters UserProfiles accordingly.
    Requires authentication.
    """
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type='business')


class CustomerUserListView(generics.ListAPIView):
    """
    API view to list all users with type 'customer'.

    Inherits from ListAPIView and filters UserProfiles accordingly.
    Requires authentication.
    """
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type='customer')
