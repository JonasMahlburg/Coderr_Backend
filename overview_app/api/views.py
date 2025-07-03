"""
API views for the overview_app providing general platform statistics
such as review counts, average ratings, business profiles, and offers.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg
from reviews_app.models import Review
from offers_app.models import Offer 
from auth_app.models import UserProfile 
from rest_framework.permissions import AllowAny

class BaseInfoAPIView(APIView):
    """
    APIView to retrieve general base information about the platform.
    Provides counts of reviews, average rating, business profiles, and offers.
    No authentication is required for access.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        try:
            review_count = Review.objects.count()
            average_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0.0
            average_rating = round(average_rating, 1)

            business_profile_count = UserProfile.objects.filter(type='business').count()
            offer_count = Offer.objects.count()

            return Response({
                "review_count": review_count,
                "average_rating": average_rating,
                "business_profile_count": business_profile_count,
                "offer_count": offer_count,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": "Interner Serverfehler."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )