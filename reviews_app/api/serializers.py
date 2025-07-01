"""
Serializers for the reviews_app handling review creation and representation.
"""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from reviews_app.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model.
    Handles creation and read-only representation of reviews,
    including reviewer, business user, rating, description, and timestamps.
    """
    reviewer = serializers.ReadOnlyField(source='reviewer.id')
    
    class Meta:

        model = Review
        fields = [
                'id',
                'business_user',
                'reviewer',
                'rating',
                'description',
                'created_at',
                'updated_at'
            ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        user = self.context['request'].user
        business_user = data.get('business_user')
        if Review.objects.filter(reviewer=user, business_user=business_user).exists():
            raise ValidationError("You have already reviewed this business user.")
        return data