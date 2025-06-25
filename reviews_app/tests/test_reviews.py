from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from reviews_app.models import Review  # oder dein Model
from datetime import datetime
from unittest.mock import patch
from auth_app.models import UserProfile  # Pfad ggf. anpassen

class ReviewListTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='TestUser', password='password123')
        UserProfile.objects.create(user=self.user, type='customer')
        self.url = reverse('review-list')

        # Optional: Erstelle Testdaten
        self.other_user = User.objects.create_user(username='Reviewer', password='1234')
        UserProfile.objects.create(user=self.other_user, type='customer')
        Review.objects.create(
            business_user=self.user,
            reviewer=self.other_user,
            rating=5,
            description="Super Arbeit!",
        )

        # Zweite Review von anderem Reviewer ODER anderem Business
        another_user = User.objects.create_user(username='Reviewer2', password='1234')
        UserProfile.objects.create(user=another_user, type='customer')

        Review.objects.create(
            business_user=self.user,
            reviewer=another_user,
            rating=4,
            description="Sehr zuverlässig!",
)

    def test_get_reviews_authenticated_returns_200(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))

    def test_get_reviews_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_reviews_with_filtering_and_ordering(self):
        Review.objects.all().delete()
        Review.objects.create(
            business_user=self.user,
            reviewer=self.other_user,
            rating=5,
            description="Gefiltert"
            )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {
            'reviewer_id': self.other_user.id,
            'business_user_id': self.user.id,
            'ordering': 'rating'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for review in response.data:
            self.assertEqual(review['reviewer'], self.other_user.id, msg=f"Falscher Reviewer: {review}")

    def test_internal_server_error_simulation_returns_500(self):
        # Hier simulieren wir einen Serverfehler z. B. durch temporäres Mocking
        from unittest.mock import patch
        self.client.force_authenticate(user=self.user)
        with patch('reviews_app.api.views.ReviewViewSet.list', side_effect=Exception("Unexpected error")):
            with self.assertRaises(Exception) as context:
                self.client.get(self.url)
            self.assertEqual(str(context.exception), "Unexpected error")


class ReviewCreateTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        # Nutzer: Business & Kunde
        self.business_user = User.objects.create_user(username='Business', password='pass')
        self.customer_user = User.objects.create_user(username='Customer', password='pass')
        UserProfile.objects.create(user=self.customer_user, type='customer')

        self.url = reverse('review-list')

        self.valid_payload = {
            "business_user": self.business_user.id,
            "rating": 5,
            "description": "Top Service!"
        }

    def test_create_review_success_201(self):
        Review.objects.all().delete()
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("rating"), 5)

    def test_create_review_unauthenticated_401(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_without_customer_profile_401(self):
        # Simuliere Nutzer ohne Kunden-Profil
        user = User.objects.create_user(username='NotCustomer', password='pass')
        self.client.force_authenticate(user=user)
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_twice_for_same_business_403(self):
        self.client.force_authenticate(user=self.customer_user)

        # Erste Bewertung
        self.client.post(self.url, self.valid_payload, format='json')

        # Zweite Bewertung für denselben business_user
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_invalid_payload_400(self):
        self.client.force_authenticate(user=self.customer_user)
        payload = {
            "business_user": "",  # ungültig
            "rating": 99,  # ggf. zu hoch
            "description": ""
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_internal_server_error_simulated_500(self):
        Review.objects.all().delete()
        self.client.force_authenticate(user=self.customer_user)
        with patch('reviews_app.api.views.ReviewViewSet.create', side_effect=Exception("Server down")):
            with self.assertRaises(Exception) as context:
                self.client.post(self.url, self.valid_payload, format='json')
            self.assertEqual(str(context.exception), "Server down")