from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from auth_app.models import UserProfile
from rest_framework import status
from django.urls import reverse

class OrdersAPITests(APITestCase):

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


    def test_get_order(self):
        url = 'http://127.0.0.1:8000/api/orders/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # def test_post_order(self):
 
