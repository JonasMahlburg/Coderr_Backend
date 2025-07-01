"""
Models for the reviews_app representing user reviews
between customers and business users, including validation
to prevent self-reviews and duplicate reviews.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from auth_app.models import UserProfile

class Review(models.Model):
    """
    Model representing a review from a customer to a business user.

    Fields:
    - business_user: The user being reviewed.
    - reviewer: The customer writing the review.
    - rating: Numeric rating score.
    - description: Optional text describing the review.
    - created_at: Timestamp when the review was created.
    - updated_at: Timestamp when the review was last updated.

    Constraints:
    - Unique together on (business_user, reviewer) to prevent duplicates.
    - Validation to prevent users reviewing themselves.
    - Only customers can write reviews.
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
        unique_together = ('business_user', 'reviewer')
        ordering = ['-updated_at']
        
    def clean(self):
        if self.business_user == self.reviewer:
            raise ValidationError("Benutzer können sich nicht selbst bewerten.")
        profile = getattr(self.reviewer, 'userprofile', None)
        if not profile or profile.type != 'customer':
            raise ValidationError("Nur Kunden mit Profil dürfen Bewertungen schreiben.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review von {self.reviewer.username} für {self.business_user.username} ({self.rating} Sterne)"