from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from auth_app.models import UserProfile
from rest_framework import status


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



