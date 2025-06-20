from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework import status


class registrationTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    
    def test_post_registration(self):
        url = 'http://127.0.0.1:8000/api/registration/'
        data = {
                "username": "exampleUsername",
                "email": "example@mail.de",
                "password": "examplePassword",
                "repeated_password": "examplePassword",
                "type": "customer"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class negativRegistrationTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='newuser', email='example@mail.de', password='newpassword123')
        self.token = Token.objects.create(user= self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION= 'Token ' + self.token.key)
        # self.user = User.objects.create_user(username='newuser', email='example@mail.de', password='12345678')
    
    def test_post_allready_existing_registration(self):
        url = 'http://127.0.0.1:8000/api/registration/'
        data = {
                "username": "newuser",
                "email": "example@mail.de",
                "password": "newpassword123",
                "repeated_password": "newpassword123",
                "type": "customer"
        }
        print(User.objects.all())
        response = self.client.post(url, data, format='json')
        print(response.status_code)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_duplicate_email_registration(self):
        url = 'http://127.0.0.1:8000/api/registration/' # oder deine URL direkt
        data = {
            "username": "Testname",
            "email": "duplicate@example.com",
            "password": "securepass123",
            "repeated_password": "securepass123",
            "type": "customer"
        }

        # 1. Erste Registrierung klappt
        response1 = self.client.post(url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # 2. Zweiter Versuch mit gleicher E-Mail sollte fehlschlagen
        response2 = self.client.post(url, data, format='json')
        print(response2.data)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)