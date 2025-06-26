from rest_framework import generics, status
from django.contrib.auth.models import User
from auth_app.models import UserProfile
from .serializers import RegistrationSerializer, UsernameAuthTokenSerializer, UserProfileSerializer, CustomerProfileSerializer, BusinessProfileSerializer
from .permissions import IsOwner, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response


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


# class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
#     """
#     API view to retrieve, update, or delete a specific user profile by ID.

#     Inherits from RetrieveUpdateDestroyAPIView to provide full CRUD support
#     for individual user profiles. Uses the RegistrationSerializer.

#     Methods:
#         get(): Retrieves a user profile by ID.
#         put(): Updates a user profile by ID.
#         delete(): Deletes a user profile by ID.
#     """
#     queryset = UserProfile.objects.all()
#     serializer_class = UserProfileSerializer
#     permission_classes = [IsOwner]

#     def get_object(self):
#         user_id = self.kwargs['pk']
#         obj = generics.get_object_or_404(UserProfile, user__id=user_id)
#         self.check_object_permissions(self.request, obj)  # <-- wichtig!
#         return obj


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
        # It's crucial to check object permissions here for security.
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
                # 'type' : saved_account.userprofile.type
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
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type='business')

class CustomerUserListView(generics.ListAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type='customer')





#--------------------------------------Gemini------------------------------------------

# from rest_framework import viewsets, mixins, status
# from django.contrib.auth.models import User # This might not be directly needed depending on how UserProfile is linked to User.
# from auth_app.models import UserProfile
# from .serializers import (
#     RegistrationSerializer,
#     UsernameAuthTokenSerializer,
#     UserProfileSerializer,
#     CustomerProfileSerializer,
#     BusinessProfileSerializer
# )
# from .permissions import IsOwner, IsAuthenticated
# from rest_framework.decorators import action # For custom actions within Viewsets
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny
# from rest_framework.authtoken.models import Token
# from django.shortcuts import get_object_or_404 # A better alternative to generics.get_object_or_404

# # Important Note: ObtainAuthToken is an APIView that creates tokens for a User.
# # Since we are moving the login logic into a ViewSet, ObtainAuthToken itself is no longer needed,
# # but its logic is replicated within the CustomAuthViewSet.

# class UserProfileViewSet(viewsets.ModelViewSet):
#     """
#     A ViewSet for viewing and editing user profiles.
#     This ViewSet combines the functionality of UserProfileList and UserProfileDetail.
#     It provides 'list', 'create', 'retrieve', 'update', 'partial_update', and 'destroy' actions.
#     Additionally, a 'register' action for user registration is included.
#     """
#     queryset = UserProfile.objects.all()
#     # The default serializer is initially set here, but overridden by get_serializer_class.
#     serializer_class = UserProfileSerializer
#     # Default permission for the ViewSet. Dynamically adjusted in get_permissions.
#     permission_classes = [IsAuthenticated]

#     def get_serializer_class(self):
#         """
#         Returns the appropriate serializer class based on the current action.
#         For the 'create' action (in the context of standard ModelViewSet creation) and
#         for the 'register' action, we use RegistrationSerializer.
#         Otherwise, we use UserProfileSerializer.
#         """
#         if self.action in ['create', 'register']:
#             return RegistrationSerializer
#         return UserProfileSerializer

#     def get_permissions(self):
#         """
#         Returns the list of permissions that this view requires.
#         Permissions are dynamically adjusted based on the action:
#         - 'create' (for general creation via ModelViewSet) and 'register' (custom action): AllowAny
#         - 'retrieve', 'update', 'partial_update', 'destroy': IsOwner (as these are detail views)
#         - 'list': IsAuthenticated (as this is a list of all profiles)
#         """
#         if self.action in ['create', 'register']:
#             self.permission_classes = [AllowAny]
#         elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
#             # For detail views, the user must be the owner of the profile.
#             self.permission_classes = [IsOwner]
#         else: # For the 'list' action
#             self.permission_classes = [IsAuthenticated]
#         return super().get_permissions()

#     def get_object(self):
#         """
#         Overrides the default get_object method to find UserProfile by user_id.
#         This corresponds to the logic you had in UserProfileDetail.
#         """
#         # If 'pk' (Primary Key) is present in kwargs, it attempts to find
#         # the UserProfile via the linked user__id.
#         if 'pk' in self.kwargs:
#             user_id = self.kwargs['pk']
#             obj = get_object_or_404(UserProfile, user__id=user_id)
#             # Important: After fetching the object, check object permissions.
#             self.check_object_permissions(self.request, obj)
#             return obj
#         # For actions like 'list' or 'create' that do not require a specific object,
#         # the default get_object method of the ModelViewSet is called.
#         return super().get_object()

#     @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
#     def register(self, request):
#         """
#         Custom action for user registration.
#         This method replicates the functionality of your original RegistrationView.
#         It creates a new user and generates an authentication token.
#         """
#         serializer = self.get_serializer(data=request.data) # get_serializer uses get_serializer_class
#         if serializer.is_valid():
#             # Saves the new User created by the RegistrationSerializer.
#             saved_account = serializer.save()
#             # Creates or gets the authentication token for the new User.
#             token, created = Token.objects.get_or_create(user=saved_account)
#             data = {
#                 'token': token.key,
#                 'username': f"{saved_account.first_name} {saved_account.last_name}".strip(),
#                 'email': saved_account.email,
#                 'user_id': saved_account.id,
#                 # 'type' : saved_account.userprofile.type # Commented out as userprofile might not exist yet
#             }
#             return Response(data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CustomAuthViewSet(viewsets.ViewSet):
#     """
#     A ViewSet for custom authentication actions like logging in.
#     Since this ViewSet does not directly manage a model (no CRUD operations),
#     viewsets.ViewSet is the appropriate base class.
#     """
#     permission_classes = [AllowAny] # The login function should be accessible to everyone.

#     @action(detail=False, methods=['post'], url_path='login')
#     def login(self, request):
#         """
#         Custom action for user login using token authentication.
#         This method replicates the functionality of your original CustomLogInView.
#         """
#         serializer = UsernameAuthTokenSerializer(
#             data=request.data,
#             context={'request': request}
#         )

#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             token, created = Token.objects.get_or_create(user=user)
#             username = f"{user.first_name} {user.last_name}".strip()
#             data = {
#                 'token': token.key,
#                 'username': username,
#                 'email': user.email,
#                 'user_id': user.id,
#             }
#             return Response(data)
#         else:
#             return Response(
#                 {'error': 'Invalid username or password'},
#                 status=status.HTTP_400_BAD_REQUEST)


# class BusinessUserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     """
#     A ViewSet for listing user profiles of type 'business'.
#     Uses ListModelMixin to provide the 'list' action,
#     and GenericViewSet as the base class.
#     """
#     serializer_class = BusinessProfileSerializer
#     permission_classes = [IsAuthenticated] # Only authenticated users can view this list.

#     def get_queryset(self):
#         """
#         Returns the queryset for business user profiles.
#         """
#         return UserProfile.objects.filter(type='business')


# class CustomerUserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     """
#     A ViewSet for listing user profiles of type 'customer'.
#     Similar to BusinessUserViewSet, but for customer profiles.
#     """
#     serializer_class = CustomerProfileSerializer
#     permission_classes = [IsAuthenticated] # Only authenticated users can view this list.

#     def get_queryset(self):
#         """
#         Returns the queryset for customer user profiles.
#         """
#         return UserProfile.objects.filter(type='customer')