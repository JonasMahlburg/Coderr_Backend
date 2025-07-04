"""
This script populates the Django database with sample data for testing purposes.
It creates users (business and customer), offers with details, orders, and reviews,
ensuring a basic set of interconnected data exists.
"""

# Standard library imports
import os
import random

# Third-party imports
import django
from django.contrib.auth.models import User

# Local application imports
from auth_app.models import UserProfile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from reviews_app.models import Review


# --- Django Setup ---
# Set the Django settings module and configure Django.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


# --- Clear Existing Data ---
# Delete all existing data from the relevant models to ensure a clean slate
# for each run of the seeding script.
Order.objects.all().delete()
Review.objects.all().delete() # Ensure reviews are deleted before users/profiles
Offer.objects.all().delete()
UserProfile.objects.all().delete()
User.objects.all().delete()


# --- Create Business Users and Offers ---
# Generate 5 business users, each with a UserProfile and multiple offers.
business_users = []
for i in range(1, 6):
    user = User.objects.create_user(
        username=f'business{i}',
        email=f'business{i}@mail.com',
        password='testpass'
    )
    business = UserProfile.objects.create(
        user=user,
        type='business',
        description=f'This is Business {i}',
        location=f'City {i}'
    )
    business_users.append(business)

    # Each business creates two offers: one 'basic' and one 'premium'
    for j, offer_type in enumerate(["basic", "premium"], start=1):
        offer = Offer.objects.create(
            user=business.user,
            title=f"Offer {j} from {user.username}",
            description=f"This is a {offer_type} offer from {user.username}.",
            offer_type=offer_type
        )
        # Create a detail for each offer
        OfferDetail.objects.create(
            offer=offer,
            title=f"{offer.title} Detail",
            revisions=random.randint(1, 5),
            delivery_time_in_days=random.randint(1, 14),
            price=random.choice([99.99, 149.99, 199.99]),
            features=["Feature A", "Feature B", "Feature C"],
            offer_type=offer_type
        )


# --- Create Customer Users ---
# Generate 10 customer users with their respective UserProfiles.
customer_users = []
for i in range(1, 11):
    user = User.objects.create_user(
        username=f'customer{i}',
        email=f'customer{i}@mail.com',
        password='testpass'
    )
    customer = UserProfile.objects.create(
        user=user,
        type='customer',
        tel=f'+49 170 {random.randint(1000000, 9999999)}',
        location=f'Location {i}'
    )
    customer_users.append(customer)


# --- Create Sample Orders ---
# Randomly create orders for some customers.
# Not all customers will place an order.
used_customers_for_orders = set() # Renamed for clarity: tracks customers who placed orders
for customer_profile in customer_users: # Renamed for clarity
    if random.choice([True, False]): # 50% chance to create an order
        # Select a random offer and one of its details
        offer = random.choice(Offer.objects.all())
        # Ensure the offer has details before trying to select one
        if offer.details.exists():
            detail = random.choice(list(offer.details.all()))
            Order.objects.create(
                customer=customer_profile.user,
                offer=offer,
                ordered_detail=detail,
                status=random.choice([
                    'pending', 'accepted', 'completed',
                    'cancelled', 'in_progress'
                ]),
                quantity=random.randint(1, 3),
                price_at_order=detail.price
            )
            used_customers_for_orders.add(customer_profile)


# --- Create Sample Reviews ---
# Randomly create reviews from customers to businesses.
# Ensures no duplicate reviews from the same customer to the same business.
created_reviews = set() # Tracks (reviewer_id, business_user_id) pairs
for customer_profile in customer_users: # Renamed for clarity
    if random.choice([True, False]): # 50% chance to write a review
        business_profile = random.choice(business_users) # Renamed for clarity
        
        # Ensure a customer doesn't review themselves
        # and doesn't review the same business twice
        key = (customer_profile.user.id, business_profile.user.id)
        if key not in created_reviews and \
           customer_profile.user != business_profile.user: # Line break for PEP8
            Review.objects.create(
                reviewer=customer_profile.user,
                business_user=business_profile.user,
                rating=random.randint(1, 5),
                description=random.choice([
                    "Very satisfied!",
                    "Could be better.",
                    "Top performance!",
                    "Not recommended.",
                    "Would buy again.",
                ])
            )
            created_reviews.add(key)


print("Test data has been successfully created.")
            