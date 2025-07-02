from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from reviews_app.models import Review
from unittest.mock import patch
from auth_app.models import UserProfile

class ReviewListTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='TestUser', password='password123')
        UserProfile.objects.create(user=self.user, type='customer')
        self.url = reverse('review-list')

      
        self.other_user = User.objects.create_user(username='Reviewer', password='1234')
        UserProfile.objects.create(user=self.other_user, type='customer')
        Review.objects.create(
            business_user=self.user,
            reviewer=self.other_user,
            rating=5,
            description="Super Arbeit!",
        )

       
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
        
        from unittest.mock import patch
        self.client.force_authenticate(user=self.user)
        with patch('reviews_app.api.views.ReviewViewSet.list', side_effect=Exception("Unexpected error")):
            with self.assertRaises(Exception) as context:
                self.client.get(self.url)
            self.assertEqual(str(context.exception), "Unexpected error")


class ReviewCreateTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

     
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
       
        user = User.objects.create_user(username='NotCustomer', password='pass')
        self.client.force_authenticate(user=user)
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_twice_for_same_business_403(self):
        self.client.force_authenticate(user=self.customer_user)

        self.client.post(self.url, self.valid_payload, format='json')

        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_invalid_payload_400(self):
        self.client.force_authenticate(user=self.customer_user)
        payload = {
            "business_user": "",
            "rating": 99,
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

from rest_framework import status

class ReviewPermissionTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.customer_user = User.objects.create_user(username='customer', password='pass')
        UserProfile.objects.create(user=self.customer_user, type='customer')

        self.non_customer_user = User.objects.create_user(username='noncustomer', password='pass')

        self.business_user = User.objects.create_user(username='business', password='pass')

        self.url = reverse('review-list')

        self.review_data = {
            "business_user": self.business_user.id,
            "rating": 4,
            "description": "Test Review"
        }

    def test_all_authenticated_can_read_reviews(self):
        Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=5, description="Good")

        self.client.force_authenticate(user=self.non_customer_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))

    def test_non_customer_cannot_create_review(self):
        self.client.force_authenticate(user=self.non_customer_user)
        response = self.client.post(self.url, self.review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_can_create_review(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(self.url, self.review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_only_owner_can_edit_or_delete_review(self):
        review = Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=5, description="Owner Review")
        edit_url = reverse('review-detail', kwargs={'pk': review.id})

        self.client.force_authenticate(user=self.non_customer_user)
        patch_response = self.client.patch(edit_url, {"rating": 3}, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.customer_user)
        patch_response = self.client.patch(edit_url, {"rating": 4}, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.non_customer_user)
        delete_response = self.client.delete(edit_url)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.customer_user)
        delete_response = self.client.delete(edit_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        