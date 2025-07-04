"""
API views for the overview_app providing general platform statistics.

Includes endpoints for retrieving aggregated data such as review counts,
average ratings, number of business profiles, and number of available offers.
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
    API view to retrieve general base information about the platform.

    Returns statistics including total reviews, average rating, number of
    business profiles, and total offer count. Publicly accessible without authentication.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """
        Handles GET requests and returns platform statistics in JSON format.

        Returns:
            Response: A JSON response containing review count, average rating,
            business profile count, and offer count.
        """
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