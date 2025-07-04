from django.urls import reverse
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from auth_app.models import UserProfile
from rest_framework import status
from decimal import Decimal

"""
Test suite for Order API endpoints.

Covers creation, retrieval, update, deletion, and custom endpoints for order counts.
Includes both customer and business user scenarios.
"""

class OrdersAPITests(APITestCase):
    """
    End-to-end tests for order-related API functionality.

    Ensures business and customer users can interact with the API as expected.
    """

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
        """
        Test retrieving the list of orders returns HTTP 200.
        """
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_post_order(self):
        """
        Test creating a new order using offer_detail_id returns HTTP 201 and correct fields.
        """
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

        self.token.delete()
        token = Token.objects.create(user=self.customer_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse('order-list')
        data = {
            "offer_detail_id": detail.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Logo & Visitenkarte")
        self.assertEqual(Decimal(response.data['price']), Decimal('150.00'))
        self.assertIn(response.data['offer_type'], ["basic", "", None])
        self.assertEqual(response.data['status'], "in_progress")

    def test_patch_order_status_as_business_user(self):
        """
        Test a business user can update the status of an order to 'completed'.
        """

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

        order = Order.objects.create(
            customer=self.customer_user,
            offer=offer,
            ordered_detail=detail,
            price_at_order=detail.price,
            status='in_progress'
        )

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        url = reverse('order-detail', kwargs={'pk': order.id})
        response = self.client.patch(url, {'status': 'completed'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

    def test_delete_order(self):
        """
        Test a business user can delete an order, and it no longer exists.
        """
        offer = Offer.objects.create(
            user=self.business_user,
            title="Angebot zum Löschen",
            description="Testbeschreibung",
            offer_type="basic"
        )
        detail = OfferDetail.objects.create(
            offer=offer,
            title="Detail zum Löschen",
            price=100,
            delivery_time_in_days=3,
            revisions=2,
            features=["Feature A"]
        )
        order = Order.objects.create(
            customer=self.customer_user,
            offer=offer,
            ordered_detail=detail,
            price_at_order=detail.price,
            status='in_progress'
        )

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('order-detail', kwargs={'pk': order.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order.id).exists())

    def test_get_order_count_for_business_user(self):
        """
        Test the API returns the correct count of in-progress orders for a business user.
        """

        offer = Offer.objects.create(
            user=self.business_user,
            title="Website Design",
            description="Komplettes Webpaket",
            offer_type="premium"
        )
        detail = OfferDetail.objects.create(
            offer=offer,
            title="Komplett-Paket",
            price=2000,
            delivery_time_in_days=14,
            revisions=5,
            features=["Webdesign", "Hosting", "Support"]
        )

        for order_status in ['in_progress', 'in_progress', 'in_progress', 'completed']:
            Order.objects.create(
                customer=self.customer_user,
                offer=offer,
                ordered_detail=detail,
                price_at_order=detail.price,
                status=order_status
            )

        token = Token.objects.create(user=self.customer_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = f'/api/order-count/{self.business_user.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 3)
   
    def test_get_completed_order_count_for_business_user(self):
        """
        Test the API returns the correct count of completed orders for a business user.
        """

        offer = Offer.objects.create(
            user=self.business_user,
            title="SEO Paket",
            description="Komplettoptimierung",
            offer_type="standard"
        )
        detail = OfferDetail.objects.create(
            offer=offer,
            title="SEO Advanced",
            price=500,
            delivery_time_in_days=7,
            revisions=2,
            features=["OnPage", "OffPage"]
        )

        for s in ['completed', 'completed', 'in_progress']:
            Order.objects.create(
                customer=self.customer_user,
                offer=offer,
                ordered_detail=detail,
                price_at_order=detail.price,
                status=s
            )

        token = Token.objects.create(user=self.customer_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = f'/api/completed-order-count/{self.business_user.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 2)
        