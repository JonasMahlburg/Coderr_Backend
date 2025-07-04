from django.db import models
from django.contrib.auth.models import User


class Offer(models.Model):
    """
    Represents an offer created by a user.

    Attributes:
        user (ForeignKey): The user who created the offer.
        title (str): The title of the offer.
        image (ImageField): Optional image associated with the offer.
        description (str): Detailed description of the offer.
        created_at (datetime): Timestamp when the offer was created.
        updated_at (datetime): Timestamp when the offer was last updated.
        offer_type (str): The type/category of the offer.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offer_images/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    offer_type = models.CharField(
        max_length=20,
        choices=OFFER_TYPE_CHOICES,
        default='basic'
    )


class OfferDetail(models.Model):
    """
    Represents detailed information about a specific offer.

    Attributes:
        offer (ForeignKey): The offer to which these details belong.
        title (str): Title of the detail entry.
        revisions (int): Number of revisions included.
        delivery_time_in_days (int): Estimated delivery time in days.
        price (Decimal): Price of the offer detail.
        features (list): List of features as JSON.
        offer_type (str): Type/category of the offer detail.
    """

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
