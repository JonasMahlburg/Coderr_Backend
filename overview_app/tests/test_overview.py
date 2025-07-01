from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from reviews_app.models import Review
from offers_app.models import Offer
from auth_app.models import UserProfile
from django.contrib.auth.models import User

class BaseInfoAPITests(APITestCase):
    def setUp(self):
        user1 = User.objects.create(username="user1")
        user2 = User.objects.create(username="user2")
        user3 = User.objects.create(username="user3")

        UserProfile.objects.create(user=user1, type="customer")
        UserProfile.objects.create(user=user2, type="business")
        UserProfile.objects.create(user=user3, type="customer")

        Review.objects.create(business_user=user2, reviewer=user1, rating=4, description="Gut!")
        Review.objects.create(business_user=user2, reviewer=user3, rating=5, description="Top!")

        Offer.objects.create(user=user2, title="Angebot 1", description="Test")
        Offer.objects.create(user=user2, title="Angebot 2", description="Test")

        self.url = "/api/base-info/"

    def test_base_info_returns_correct_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = {
            "review_count": 2,
            "average_rating": 4.5,
            "business_profile_count": 1,
            "offer_count": 2
        }

        self.assertEqual(response.data, expected)

    def test_base_info_accessible_without_authentication(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        