from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from auth_app.models import UserProfile
from rest_framework import status
from django.urls import reverse

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
        url = 'http://127.0.0.1:8000/api/offers/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_offers(self):
        url = 'http://127.0.0.1:8000/api/offers/'
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

    def test_patch_offer(self):
        # 1. Angebot anlegen
        create_url = 'http://127.0.0.1:8000/api/offers/'
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

        # 2. ID des erstellten Angebots holen
        offer_id = create_response.data['id']

        # 3. PATCH-Daten vorbereiten
        patch_url = f'http://127.0.0.1:8000/api/offers/{offer_id}/'
        patch_data = {
            "description": "Neue, verbesserte Beschreibung"
        }

        # 4. PATCH-Request senden
        patch_response = self.client.patch(patch_url, patch_data, format='json')

        # 5. Ergebnis prüfen
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['description'], "Neue, verbesserte Beschreibung")

    def test_delete_offer(self):
        # 1. Angebot anlegen
        create_url = 'http://127.0.0.1:8000/api/offers/'
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
        delete_url = f'http://127.0.0.1:8000/api/offers/{offer_id}/'

        # 2. DELETE-Anfrage senden
        delete_response = self.client.delete(delete_url)

        # 3. Ergebnis prüfen
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # 4. Sicherstellen, dass das Angebot wirklich weg ist
        get_response = self.client.get(delete_url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)