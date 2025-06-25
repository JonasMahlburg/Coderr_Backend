from rest_framework import serializers
from reviews_app.models import Review

class ReviewSerializer(serializers.ModelSerializer):
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