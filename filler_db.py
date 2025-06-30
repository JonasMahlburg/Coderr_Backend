import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from auth_app.models import UserProfile 
from orders_app.models import Order
from reviews_app.models import Review
from offers_app.models import Offer, OfferDetail
import random

# Erst alle Daten löschen
Order.objects.all().delete()
Offer.objects.all().delete()
UserProfile.objects.all().delete()
User.objects.all().delete()

# Business Accounts anlegen
business_users = []
for i in range(1, 6):
    user = User.objects.create_user(username=f'business{i}', email=f'business{i}@mail.com', password='testpass')
    business = UserProfile.objects.create(
        user=user,
        type='business',
        description=f'Das ist Business {i}',
        location=f'Stadt {i}'
    )
    business_users.append(business)

    # Zwei Angebote pro Business
    for j, offer_type in enumerate(["basic", "premium"], start=1):
        offer = Offer.objects.create(
            user=business.user,
            title=f"Angebot {j} von {user.username}",
            description=f"Dies ist ein {offer_type} Angebot von {user.username}.",
            offer_type=offer_type
        )
        OfferDetail.objects.create(
            offer=offer,
            title=f"{offer.title} Detail",
            revisions=random.randint(1, 5),
            delivery_time_in_days=random.randint(1, 14),
            price=random.choice([99.99, 149.99, 199.99]),
            features=["Feature A", "Feature B", "Feature C"],
            offer_type=offer_type
        )

# Customer Accounts anlegen
customer_users = []
for i in range(1, 11):
    user = User.objects.create_user(username=f'customer{i}', email=f'customer{i}@mail.com', password='testpass')
    customer = UserProfile.objects.create(
        user=user,
        type='customer',
        tel=f'+49 170 {random.randint(1000000, 9999999)}',
        location=f'Ort {i}'
    )
    customer_users.append(customer)


# Bestellungen zufällig verteilen (jeder max. eine Bestellung)
used_customers = set()
for customer in customer_users:
    if random.choice([True, False]):
        offer = random.choice(Offer.objects.all())
        detail = random.choice(list(offer.details.all()))
        Order.objects.create(
            customer=customer.user,
            offer=offer,
            ordered_detail=detail,
            status=random.choice(['pending', 'accepted', 'completed', 'cancelled', 'in_progress']),
            quantity=random.randint(1, 3),
            price_at_order=detail.price
        )
        used_customers.add(customer)

print("Testdaten wurden erfolgreich erstellt.")

# Reviews zufällig erstellen (nur von Kunden an Businesses, max. eine pro Kombination)
created_reviews = set()
for customer in customer_users:
    if random.choice([True, False]):
        business = random.choice(business_users)
        key = (customer.user.id, business.user.id)
        if key not in created_reviews and customer.user != business.user:
            Review.objects.create(
                reviewer=customer.user,
                business_user=business.user,
                rating=random.randint(1, 5),
                description=random.choice([
                    "Sehr zufrieden!",
                    "Könnte besser sein.",
                    "Top Leistung!",
                    "Nicht empfehlenswert.",
                    "Würde wieder kaufen."
                ])
            )
            created_reviews.add(key)