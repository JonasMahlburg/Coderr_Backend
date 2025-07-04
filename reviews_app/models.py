"""
Models for the reviews_app representing user reviews
between customers and business users, including validation
to prevent self-reviews and duplicate reviews.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Review(models.Model):
    """
    Model representing a review from a customer to a business user.

    Fields:
    - business_user: The user being reviewed (the business).
    - reviewer: The customer writing the review.
    - rating: Numeric rating score (e.g., 1-5).
    - description: Optional text describing the review.
    - created_at: Timestamp when the review was created.
    - updated_at: Timestamp when the review was last updated.

    Constraints:
    - Unique together on (business_user, reviewer) to prevent duplicate reviews
      from the same reviewer to the same business user.
    - Validation to prevent users from reviewing themselves.
    - Only users with a 'customer' UserProfile type can write reviews.
    """
    business_user = models.ForeignKey(
        User,
        related_name='received_reviews',
        on_delete=models.CASCADE
    )
    reviewer = models.ForeignKey(
        User,
        related_name='written_reviews',
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for the Review model.
        Defines unique constraints and default ordering.
        """
        unique_together = ('business_user', 'reviewer')
        ordering = ['-updated_at']

    def clean(self):
        """
        Performs custom validation for the Review instance.
        Ensures a user cannot review themselves and only customers can write reviews.
        """
        if self.business_user == self.reviewer:
            raise ValidationError("Users cannot review themselves.")

        profile = getattr(self.reviewer, 'userprofile', None)
        if not profile or profile.type != 'customer':
            raise ValidationError("Only customers with a profile are allowed to write reviews.")

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to include full model validation
        before saving the instance to the database.
        """
        self.full_clean()  # Calls clean() and validates all fields
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a string representation of the review, including the reviewer,
        business user, and rating.
        """
        return (
            f"Review from {self.reviewer.username} for "
            f"{self.business_user.username} ({self.rating} stars)"
        )
    