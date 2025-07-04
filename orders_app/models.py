# orders_app/models.py (assuming this is the file)

from django.db import models
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail


class Order(models.Model):
    """
    Represents a customer order for a specific offer and its detail.
    Tracks status, quantity, price at order time, and timestamps.
    """
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders'
    )
    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name='orders'
    )
    ordered_detail = models.ForeignKey(
        OfferDetail, on_delete=models.CASCADE, related_name='orders_for_detail'
    )

    # Status choices for an order
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('in_progress', 'in_Progress'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for the Order model.
        Defines verbose names and default ordering.
        """
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

    def __str__(self):
        """
        Returns a string representation of the order, including its ID,
        associated offer title, detail title, and customer username.
        """
        return (
            f"Order {self.id} for Offer '{self.offer.title}' "
            f"(Detail: {self.ordered_detail.title}) by {self.customer.username}"
        )

    def get_total_price(self):
        """
        Calculates and returns the total price of the order based on
        the price at order time and quantity.
        """
        return self.price_at_order * self.quantity