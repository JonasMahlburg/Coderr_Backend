from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from auth_app.models import UserProfile
from rest_framework import status
import uuid


class UserProfileAPITests(APITestCase):
    """
    Test suite for endpoints related to user profile access and updates,
    including business and customer profiles.
    """

    def setUp(self):
        """
        Set up test users and associated profiles before each test.
        """
        self.business_user = User.objects.create_user(username='business_user', password='test123')
        self.customer_user = User.objects.create_user(username='customer_user', password='test123')
        self.business_profile = UserProfile.objects.create(
            user=self.business_user,
            type='business',
            location='Berlin',
            tel='123456789',
            description='Test description',
            working_hours='9-17'
        )
        self.customer_profile = UserProfile.objects.create(
            user=self.customer_user,
            type='customer',
            file='profile.jpg'
        )
        self.token = Token.objects.create(user=self.business_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_business_profiles(self):
        """
        Test that only business profiles are returned from the /business/ endpoint.
        """
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(p['type'] == 'business' for p in response.data))
        for profile in response.data:
            for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
                self.assertIsNotNone(profile.get(field))

    def test_get_customer_profiles(self):
        """
        Test that only customer profiles are returned from the /customer/ endpoint.
        """
        response = self.client.get('/api/profiles/customer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(p['type'] == 'customer' for p in response.data))
        for profile in response.data:
            for field in ['first_name', 'last_name', 'file']:
                self.assertIsNotNone(profile.get(field))

    def test_get_single_profile(self):
        """
        Test retrieving a single profile returns correct user data.
        """
        url = f'/api/profile/{self.business_profile.pk}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.business_user.id)

    def test_patch_own_profile(self):
        """
        Test that a user can update their own profile successfully.
        """
        url = f'/api/profile/{self.business_profile.pk}/'
        payload = {
            'first_name': 'NewName',
            'last_name': 'NewLast',
            'location': 'NewCity',
            'tel': '987654321',
            'description': 'Updated',
            'working_hours': '10-18',
            'email': 'new@example.com'
        }
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'NewName')
        self.assertEqual(response.data['email'], 'new@example.com')


class AuthTests(APITestCase):
    """
    Test suite for user authentication and registration endpoints.
    """

    def test_registration_success(self):
        """
        Test successful registration returns HTTP 201 and a user ID.
        """
        data = {
            "username": "JonasTest",
            "email": "jonas@example.com",
            "password": "strongPassword123",
            "repeated_password": "strongPassword123",
            "type": "customer"
        }
        response = self.client.post("/api/registration/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user_id", response.data)

    def test_registration_password_mismatch(self):
        """
        Test registration fails when passwords do not match.
        """
        data = {
            "username": "JonasTest",
            "email": "jonas@example.com",
            "password": "pass1",
            "repeated_password": "pass2"
        }
        response = self.client.post("/api/registration/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """
        Test login with valid credentials returns a token.
        """
        user = User.objects.create_user(username="JonasTest", password="strongPassword123")
        data = {
            "username": "JonasTest",
            "password": "strongPassword123"
        }
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_invalid_credentials(self):
        """
        Test login fails with invalid credentials.
        """
        data = {
            "username": "JonasTest",
            "password": "wrongPassword"
        }
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileTests(APITestCase):
    """
    Test suite for authenticated user profile access and modification.
    """

    def setUp(self):
        """
        Set up a test user and token for authenticated profile operations.
        """
        self.client = APIClient()
        self.username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.password = "testpassword123"
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        self.profile = UserProfile.objects.create(user=self.user, type="business")
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.detail_url = f'/api/profile/{self.profile.pk}/'

    def test_get_own_profile(self):
        """
        Test that an authenticated user can retrieve their own profile data.
        """
        response = self.client.get(self.detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.username)
        self.assertEqual(response.data['email'], self.email)
        self.assertEqual(response.data['type'], self.profile.type)

    def test_patch_profile(self):
        """
        Test that an authenticated user can update specific profile fields.
        """
        patch_data = {'location': 'New Test Location'}
        response = self.client.patch(self.detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.location, 'New Test Location')
