from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from auth_app.models import UserProfile
from rest_framework import status
from django.urls import reverse
import copy


class OffersAPITest(APITestCase):

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

    def test_get_offers(self):
        url = reverse('offer-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_offers(self):
        url = reverse('offer-list')
        data = {
            "title": "Design-Paket",
            "description": "Ein umfangreiches Design-Angebot.",
            "details": [
                {
                    "title": "Logo Design",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 199.99,
                    "features": "Individuelles Logo, 3 Entwürfe, 2 Überarbeitungen",
                    "offer_type": "graphic"
                },
                {
                    "title": "Visitenkarte",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": 99.99,
                    "features": "Beidseitig, druckfertig",
                    "offer_type": "print"
                },
                {
                    "title": "Social Media Design",
                    "revisions": 3,
                    "delivery_time_in_days": 4,
                    "price": 149.99,
                    "features": "Instagram, Facebook Templates",
                    "offer_type": "digital"
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_offer_by_id(self):
  
        create_url = reverse('offer-list')
        offer_data = {
            "title": "Einzelabruf-Angebot",
            "description": "Für GET /offers/{id}/ Test",
            "details": [
                {
                    "title": "Einzeldetail",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": 100.00,
                    "features": "Ein Feature",
                    "offer_type": "graphic"
                },
                {
                    "title": "Zusatzdetail",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 150.00,
                    "features": "Zwei Features",
                    "offer_type": "digital"
                },
                {
                    "title": "Expressdetail",
                    "revisions": 1,
                    "delivery_time_in_days": 1,
                    "price": 75.00,
                    "features": "Express Feature",
                    "offer_type": "print"
                }
            ]
        }
        create_response = self.client.post(create_url, offer_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        offer_id = create_response.data['id']

        get_url = reverse('offer-detail', kwargs={'pk': offer_id})
        get_response = self.client.get(get_url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['id'], offer_id)

    def test_patch_offer(self):

        create_url = reverse('offer-list')
        offer_data = {
            "title": "Design-Paket",
            "description": "Alte Beschreibung.",
            "details": [
                {
                    "title": "Logo Design",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 199.99,
                    "features": "Logo mit Varianten",
                    "offer_type": "graphic"
                },
                {
                    "title": "Visitenkarte",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": 99.99,
                    "features": "Vorder- und Rückseite",
                    "offer_type": "print"
                },
                {
                    "title": "Social Media",
                    "revisions": 3,
                    "delivery_time_in_days": 4,
                    "price": 149.99,
                    "features": "Templates für IG und FB",
                    "offer_type": "digital"
                }
            ]
        }
        create_response = self.client.post(create_url, offer_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        offer_id = create_response.data['id']
        patch_url = reverse('offer-detail', kwargs={'pk': offer_id})
        patch_data = {
            "description": "Neue, verbesserte Beschreibung"
        }
        patch_response = self.client.patch(patch_url, patch_data, format='json')

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['description'], "Neue, verbesserte Beschreibung")

    def test_delete_offer(self):
        create_url = reverse('offer-list')
        offer_data = {
            "title": "Löschbares Angebot",
            "description": "Wird gleich gelöscht.",
            "details": [
                {
                    "title": "Detail A",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": 50.00,
                    "features": "Basisleistung",
                    "offer_type": "graphic"
                },
                {
                    "title": "Detail B",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 75.00,
                    "features": "Zusatzleistung",
                    "offer_type": "digital"
                },
                {
                    "title": "Detail C",
                    "revisions": 1,
                    "delivery_time_in_days": 1,
                    "price": 30.00,
                    "features": "Express",
                    "offer_type": "print"
                }
            ]
        }
        create_response = self.client.post(create_url, offer_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        offer_id = create_response.data['id']
        delete_url = reverse('offer-detail', kwargs={'pk': offer_id})
        delete_response = self.client.delete(delete_url)

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        get_response = self.client.get(delete_url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)


    def test_get_offerdetail_by_id(self):
        create_url = reverse('offer-list')
        offer_data = {
            "title": "Angebot mit Detailabruf",
            "description": "Für GET /offerdetails/{id}/ Test",
            "details": [
                {
                    "title": "Ein Detail",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": 100.00,
                    "features": "Test-Feature",
                    "offer_type": "graphic"
                },
                {
                    "title": "Zweites Detail",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": 110.00,
                    "features": "Zweites Feature",
                    "offer_type": "digital"
                },
                {
                    "title": "Drittes Detail",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": 120.00,
                    "features": "Drittes Feature",
                    "offer_type": "print"
                }
            ]
        }
        create_response = self.client.post(create_url, offer_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        offer_details = create_response.data['details']
        self.assertTrue(len(offer_details) > 0)

        detail_id = offer_details[0]['id']
        detail_url = reverse('offerdetail-detail', kwargs={'pk': detail_id})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['id'], detail_id)
    
    def test_offer_filtering_by_price_and_delivery(self):
        """
        Ensure offers can be filtered using min_price, max_price,
        min_delivery and max_delivery query parameters.
        """
        create_url = reverse('offer-list')
        offer_data = {
            "title": "Filterbares Angebot",
            "description": "Zum Testen von Preis- und Lieferzeit-Filtern.",
            "details": [
                {
                    "title": "Günstig & Schnell",
                    "revisions": 1,
                    "delivery_time_in_days": 1,
                    "price": 50.00,
                    "features": "Basisleistung",
                    "offer_type": "graphic"
                },
                {
                    "title": "Mittel",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 150.00,
                    "features": "Standardleistung",
                    "offer_type": "digital"
                },
                {
                    "title": "Teuer & Langsam",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 300.00,
                    "features": "Premiumleistung",
                    "offer_type": "print"
                }
            ]
        }
        create_response = self.client.post(create_url, offer_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        url = reverse('offer-list')

        response_min_price = self.client.get(url + '?min_price=200')
        self.assertEqual(response_min_price.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_min_price.data['results']), 1)

        response_max_price = self.client.get(url + '?max_price=100')
        self.assertEqual(response_max_price.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_max_price.data['results']), 1)

        response_min_delivery = self.client.get(url + '?min_delivery=4')
        self.assertEqual(response_min_delivery.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_min_delivery.data['results']), 1)

        response_max_delivery = self.client.get(url + '?max_delivery=2')
        self.assertEqual(response_max_delivery.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_max_delivery.data['results']), 1)
        
    def test_invalid_filter_values_return_400(self):
        """
        Ensure invalid filter values like non-numeric min_price or min_delivery
        return a 400 Bad Request.
        """
        url = reverse('offer-list')

        response_invalid_price = self.client.get(url + '?min_price=abc')
        self.assertEqual(response_invalid_price.status_code, status.HTTP_400_BAD_REQUEST)

        response_invalid_delivery = self.client.get(url + '?min_delivery=test')
        self.assertEqual(response_invalid_delivery.status_code, status.HTTP_400_BAD_REQUEST)

        response_multiple_invalid = self.client.get(url + '?min_price=abc&max_delivery=xyz')
        self.assertEqual(response_multiple_invalid.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_offerdetail_permissions(self):
        """
        Ensure only the owner of the offer can update or delete OfferDetails.
        Other authenticated users can read but not modify them.
        """
        create_url = reverse('offer-list')
        base_offer_data = {
            "title": "Testangebot",
            "description": "Nur Besitzer darf ändern",
            "details": [
                {
                    "title": "Detail A",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": 50.00,
                    "features": "Nur für den Ersteller editierbar",
                    "offer_type": "graphic"
                },
                {
                    "title": "Detail B",
                    "revisions": 1,
                    "delivery_time_in_days": 3,
                    "price": 60.00,
                    "features": "Zweites Feature",
                    "offer_type": "digital"
                },
                {
                    "title": "Detail C",
                    "revisions": 1,
                    "delivery_time_in_days": 1,
                    "price": 70.00,
                    "features": "Drittes Feature",
                    "offer_type": "print"
                }
            ]
        }
        create_response = self.client.post(create_url, copy.deepcopy(base_offer_data), format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        detail_id = create_response.data['details'][0]['id']
        detail_url = reverse('offerdetail-detail', kwargs={'pk': detail_id})

        patch_response = self.client.patch(detail_url, {'price': 60.00}, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(float(patch_response.data['price']), 60.0)

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)


        offer_for_other_user = copy.deepcopy(base_offer_data)
        offer_for_other_user["title"] = "Testangebot (Fremdzugriff-Test)"
        
        create_response = self.client.post(create_url, offer_for_other_user, format='json')
        
        if create_response.status_code != status.HTTP_201_CREATED:
            print("API Validation Error:", create_response.data)

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        detail_id = create_response.data['details'][0]['id']
        detail_url = reverse('offerdetail-detail', kwargs={'pk': detail_id})

        other_token = Token.objects.create(user=self.customer_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + other_token.key)

        get_response = self.client.get(detail_url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

        patch_response = self.client.patch(detail_url, {'price': 70.00}, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
