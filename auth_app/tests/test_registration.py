# from rest_framework.test import APITestCase, APIClient
# from rest_framework.authtoken.models import Token
# from django.contrib.auth.models import User
# from rest_framework import status
# from django.urls import reverse


# class registrationTests(APITestCase):

#     def setUp(self):
#         self.client = APIClient()

    
#     def test_post_registration(self):
#         url = 'http://127.0.0.1:8000/api/registration/'
#         data = {
#                 "username": "exampleUsername",
#                 "email": "example@mail.de",
#                 "password": "examplePassword",
#                 "repeated_password": "examplePassword",
#                 "type": "customer"
#         }
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# class negativRegistrationTest(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username='newuser', email='example@mail.de', password='newpassword123')
#         self.token = Token.objects.create(user= self.user)
#         self.client = APIClient()
#         self.client.credentials(HTTP_AUTHORIZATION= 'Token ' + self.token.key)
#         # self.user = User.objects.create_user(username='newuser', email='example@mail.de', password='12345678')
    
#     def test_post_allready_existing_registration(self):
#         url = 'http://127.0.0.1:8000/api/registration/'
#         data = {
#                 "username": "newuser",
#                 "email": "example@mail.de",
#                 "password": "newpassword123",
#                 "repeated_password": "newpassword123",
#                 "type": "customer"
#         }
#         print(User.objects.all())
#         response = self.client.post(url, data, format='json')
#         print(response.status_code)
#         print(response.data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


#     def test_duplicate_email_registration(self):
#         url = 'http://127.0.0.1:8000/api/registration/' # oder deine URL direkt
#         data = {
#             "username": "Testname",
#             "email": "duplicate@example.com",
#             "password": "securepass123",
#             "repeated_password": "securepass123",
#             "type": "customer"
#         }

#         # 1. Erste Registrierung klappt
#         response1 = self.client.post(url, data, format='json')
#         self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

#         # 2. Zweiter Versuch mit gleicher E-Mail sollte fehlschlagen
#         response2 = self.client.post(url, data, format='json')
#         print(response2.data)
#         self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)



from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from auth_app.models import UserProfile # Importiere UserProfile
from django.urls import reverse # Importiere reverse
import uuid # Für das Generieren einzigartiger Werte

class RegistrationTests(APITestCase):
    """
    Tests for successful user registration.
    """
    def setUp(self):
        # Initialize the API client for each test.
        self.client = APIClient()

    def test_post_registration_success(self):
        """
        Tests successful user registration with unique credentials.
        """
        # Generate unique username and email for each test run to avoid conflicts.
        unique_username = f"user_{uuid.uuid4().hex[:8]}"
        unique_email = f"email_{uuid.uuid4().hex[:8]}@example.com"

        # Define the registration data.
        data = {
            "username": unique_username,
            "email": unique_email,
            "password": "examplePassword123", # Use a strong password for consistency
            "repeated_password": "examplePassword123",
            "type": "customer"
        }
        # Use reverse() to get the URL based on the router configuration.
        # Assuming your router's basename for UserProfileViewSet is 'user-profile'
        # and the custom action is 'register'.
        url = 'http://127.0.0.1:8000/api/registration/'

        response = self.client.post(url, data, format='json')

        # Assert that registration was successful (HTTP 201 Created).
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Further assertions to ensure user and profile were created correctly
        self.assertTrue('token' in response.data)
        self.assertEqual(User.objects.filter(email=unique_email).count(), 1)
        self.assertEqual(UserProfile.objects.filter(user__email=unique_email).count(), 1)


class NegativeRegistrationTests(APITestCase):
    """
    Tests for unsuccessful user registration scenarios.
    """
    def setUp(self):
        # Initialize the API client for each test.
        self.client = APIClient()

        # Create a user for testing scenarios where a user already exists.
        # Ensure this user's details are unique or managed not to conflict with other tests
        # if other tests rely on a clean state (which is generally recommended).
        self.existing_user_email = f"existing_{uuid.uuid4().hex[:8]}@mail.de"
        self.existing_user_username = f"existing_user_{uuid.uuid4().hex[:8]}"
        self.user = User.objects.create_user(
            username=self.existing_user_username,
            email=self.existing_user_email,
            password='newpassword123'
        )
        UserProfile.objects.create(user=self.user, type="customer") # Create a profile for the existing user

        # No need to set credentials for negative registration tests usually,
        # as registration is typically allowed for unauthenticated users.
        # self.token = Token.objects.create(user= self.user)
        # self.client.credentials(HTTP_AUTHORIZATION= 'Token ' + self.token.key)
    
    def test_post_already_existing_user_data(self):
        """
        Tests registration with username and email that already exist.
        Should return HTTP 400 Bad Request.
        """
        # Data that conflicts with the user created in setUp.
        data = {
            "username": self.existing_user_username, # Conflicts with existing user
            "email": self.existing_user_email,     # Conflicts with existing user
            "password": "newpassword123",
            "repeated_password": "newpassword123",
            "type": "customer"
        }
        # Use reverse() for the URL.
        url = 'http://127.0.0.1:8000/api/registration/'

        response = self.client.post(url, data, format='json')

        # Debug prints (can be removed once tests pass consistently)
        # print(User.objects.all()) # Shows all users in the test DB
        # print(f"Status Code: {response.status_code}")
        # print(f"Response Data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Assert specific error messages for email and/or username
        self.assertIn('error', response.data)
        self.assertIn("already taken", str(response.data['error'])) # Check for either email or username error

    def test_duplicate_email_registration(self):
        """
        Tests registering the same email twice.
        The first should succeed, the second should fail with HTTP 400.
        """
        unique_username_1 = f"test_dup_user_1_{uuid.uuid4().hex[:8]}"
        unique_username_2 = f"test_dup_user_2_{uuid.uuid4().hex[:8]}"
        unique_email = f"duplicate_test_{uuid.uuid4().hex[:8]}@example.com"

        registration_data = {
            "username": unique_username_1,
            "email": unique_email,
            "password": "securepass123",
            "repeated_password": "securepass123",
            "type": "customer"
        }
        url = 'http://127.0.0.1:8000/api/registration/'

        # 1. First registration attempt (should succeed)
        response1 = self.client.post(url, registration_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Modify data for the second attempt (only username needs to change if we're testing email)
        # The email is intentionally kept the same.
        registration_data_duplicate_email = registration_data.copy()
        registration_data_duplicate_email['username'] = unique_username_2

        # 2. Second attempt with the same email (should fail)
        response2 = self.client.post(url, registration_data_duplicate_email, format='json')
        # print(f"Response2 Data (Duplicate Email): {response2.data}")
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response2.data)
        self.assertIn("This email is already taken", str(response2.data['error']))

    def test_duplicate_username_registration(self):
        """
        Tests registering the same username twice.
        The first should succeed, the second should fail with HTTP 400.
        """
        unique_username = f"test_dup_user_{uuid.uuid4().hex[:8]}"
        unique_email_1 = f"duplicate_test_email_1_{uuid.uuid4().hex[:8]}@example.com"
        unique_email_2 = f"duplicate_test_email_2_{uuid.uuid4().hex[:8]}@example.com"

        registration_data = {
            "username": unique_username,
            "email": unique_email_1,
            "password": "securepass123",
            "repeated_password": "securepass123",
            "type": "customer"
        }
        url = 'http://127.0.0.1:8000/api/registration/'

        # 1. First registration attempt (should succeed)
        response1 = self.client.post(url, registration_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Modify data for the second attempt (only email needs to change if we're testing username)
        # The username is intentionally kept the same.
        registration_data_duplicate_username = registration_data.copy()
        registration_data_duplicate_username['email'] = unique_email_2

        # 2. Second attempt with the same username (should fail)
        response2 = self.client.post(url, registration_data_duplicate_username, format='json')
        # print(f"Response2 Data (Duplicate Username): {response2.data}")
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response2.data)
        self.assertIn("This username is already taken", str(response2.data['error']))

    def test_passwords_do_not_match(self):
        """
        Tests registration when password and repeated_password do not match.
        Should return HTTP 400 Bad Request.
        """
        unique_username = f"user_nomatch_{uuid.uuid4().hex[:8]}"
        unique_email = f"email_nomatch_{uuid.uuid4().hex[:8]}@example.com"

        data = {
            "username": unique_username,
            "email": unique_email,
            "password": "password1",
            "repeated_password": "password2", # Mismatch
            "type": "customer"
        }
        url = 'http://127.0.0.1:8000/api/registration/'

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Passwords do not match')

    def test_missing_required_fields(self):
        """
        Tests registration with missing required fields.
        Should return HTTP 400 Bad Request.
        """
        # Missing 'email' and 'password'
        data = {
            "username": "missing_fields_user",
            "type": "customer"
        }
        url = 'http://127.0.0.1:8000/api/registration/'

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data) # Check if 'email' is reported as missing
        self.assertIn('password', response.data) # Check if 'password' is reported as missing
        self.assertIn('repeated_password', response.data) # Check if 'repeated_password' is reported as missing

