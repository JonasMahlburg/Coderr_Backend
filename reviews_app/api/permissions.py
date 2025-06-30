from rest_framework.permissions import BasePermission


class IsCustomerAndNotReviewedBefore(BasePermission):
    """
    Allows only authenticated users with a customer profile to create reviews.
    Additionally, the user may not have already reviewed the specified business profile.
    Only the creator of the review can edit or delete it.
    """

    def has_permission(self, request, view):
  
        if not request.user or not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'userprofile'):
            return False
        if request.user.userprofile.type != 'customer':
            return False

        if request.method == 'POST':
            business_user_id = request.data.get('business_user')
            if business_user_id:
                from reviews_app.models import Review
                if Review.objects.filter(reviewer=request.user, business_user_id=business_user_id).exists():
                    return False
        return True

    def has_object_permission(self, request, view, obj):

        if request.method in ['PATCH', 'DELETE']:
            return obj.reviewer == request.user
        return True