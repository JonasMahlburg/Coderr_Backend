from rest_framework import viewsets, status
from rest_framework.response import Response
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from .permissions import IsCustomerAndNotReviewedBefore



class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsCustomerAndNotReviewedBefore]

    def perform_create(self, serializer):
        try:
            serializer.save(reviewer=self.request.user)
        except ValidationError as e:
            raise DRFValidationError(e.message_dict)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
# class ReviewViewSet(viewsets.ModelViewSet):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer
#     permission_classes = [IsCustomerAndNotReviewedBefore]

#     def create(self, request, *args, **kwargs):
#         try:
#             return super().create(request, *args, **kwargs)
#         except Exception as e:
#             # Logging kannst du hier einbauen, falls gewünscht
#             return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)