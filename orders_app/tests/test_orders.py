from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from auth_app.models import UserProfile
from rest_framework import status
from decimal import Decimal

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
    
    def test_post_order(self):
        # Setup: Business erstellt ein Angebot + Detail
        from offers_app.models import Offer, OfferDetail

        offer = Offer.objects.create(
            user=self.business_user,
            title="Logo Design",
            description="Design Services",
            offer_type="basic"
        )
        detail = OfferDetail.objects.create(
            offer=offer,
            title="Logo & Visitenkarte",
            price=150,
            delivery_time_in_days=5,
            revisions=3,
            features=["Logo Design", "Visitenkarten"]
        )

        # Authentifiziere als customer
        self.token.delete()  # remove business token
        token = Token.objects.create(user=self.customer_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # Sende Bestellung
        url = 'http://127.0.0.1:8000/api/orders/'
        data = {
            "offer_detail_id": detail.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Logo & Visitenkarte")
        self.assertEqual(Decimal(response.data['price']), Decimal('150.00'))
        self.assertIn(response.data['offer_type'], ["basic", "", None])
        self.assertEqual(response.data['status'], "in_progress")
