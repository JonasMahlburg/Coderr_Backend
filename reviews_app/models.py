from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from auth_app.models import UserProfile

class Review(models.Model):
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
        try:
            if self.reviewer.userprofile.type != 'customer':
                raise ValidationError("Nur Kunden können Bewertungen schreiben.")
        except UserProfile.DoesNotExist:
            raise ValidationError("Nur Kunden mit Profil dürfen Bewertungen schreiben.")

    def save(self, *args, **kwargs):
        self.full_clean()  # führt clean() automatisch aus
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review von {self.reviewer.username} für {self.business_user.username} ({self.rating} Sterne)"