from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from auth_app.models import UserProfile
from rest_framework import status
import uuid

class UserProfileAPITests(APITestCase):
    def setUp(self):
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
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(p['type'] == 'business' for p in response.data))
        for profile in response.data:
            for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
                self.assertIsNotNone(profile.get(field))

    def test_get_customer_profiles(self):
        response = self.client.get('/api/profiles/customer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(p['type'] == 'customer' for p in response.data))
        for profile in response.data:
            for field in ['first_name', 'last_name', 'file']:
                self.assertIsNotNone(profile.get(field))

    def test_get_single_profile(self):
        url = f'/api/profile/{self.business_profile.pk}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.business_user.id)

    def test_patch_own_profile(self):
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
    def test_registration_success(self):
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
        data = {
            "username": "JonasTest",
            "email": "jonas@example.com",
            "password": "pass1",
            "repeated_password": "pass2"
        }
        response = self.client.post("/api/registration/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        user = User.objects.create_user(username="JonasTest", password="strongPassword123")
        data = {
            "username": "JonasTest",
            "password": "strongPassword123"
        }
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_invalid_credentials(self):
        data = {
            "username": "JonasTest",
            "password": "wrongPassword"
        }
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# class ProfileTests(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username="Jonas", password="secret123")
#         self.profile = UserProfile.objects.create(user=self.user, type="business")
#         self.client.login(username="Jonas", password="secret123")

#     def test_get_own_profile(self):
#         response = self.client.get(f"/api/profile/{self.profile.pk}/")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["id"], self.profile.pk)

#     def test_patch_profile(self):
#         response = self.client.patch(f"/api/profile/{self.profile.pk}/", {
#             "bio": "Updated bio"
#         }, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["bio"], "Updated bio")

class ProfileTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Create a user (and ensure unique data for robustness)
        self.username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.password = "testpassword123"
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

        # 2. Create a UserProfile for this user (using 'type', not 'role')
        # This fixes the TypeError you saw previously.
        self.profile = UserProfile.objects.create(user=self.user, type="business")

        # 3. Obtain a token for the user
        self.token, created = Token.objects.get_or_create(user=self.user)

        # 4. Authenticate the client with the token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Base URL for profile details (using reverse for robustness)
        self.detail_url = f'/api/profile/{self.profile.pk}/'

    def test_get_own_profile(self):
        # Now the client is authenticated, and the URL is correct
        response = self.client.get(self.detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.username)
        self.assertEqual(response.data['email'], self.email)
        self.assertEqual(response.data['type'], self.profile.type)


    def test_patch_profile(self):
        # Ensure the client is authenticated and the user is the owner
        patch_data = {'location': 'New Test Location'}
        response = self.client.patch(self.detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db() # Refresh the instance from the database
        self.assertEqual(self.profile.location, 'New Test Location')

