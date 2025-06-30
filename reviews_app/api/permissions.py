from rest_framework.permissions import BasePermission


class IsCustomerAndNotReviewedBefore(BasePermission):
    """
    Erlaubt nur authentifizierten Nutzern mit Kundenprofil eine Bewertung abzugeben.
    Außerdem darf der Nutzer noch keine Bewertung für das angegebene Geschäftsprofil abgegeben haben.
    Nur der Ersteller darf eine Bewertung bearbeiten oder löschen.
    """

    def has_permission(self, request, view):
        # Authentifizierter Nutzer und Kundenprofil erforderlich
        if not request.user or not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'userprofile'):
            return False
        if request.user.userprofile.type != 'customer':
            return False

        if request.method == 'POST':
            business_user_id = request.data.get('business_user')
            if business_user_id:
                from reviews_app.models import Review  # Import hier, um zirkuläre Imports zu vermeiden
                if Review.objects.filter(reviewer=request.user, business_user_id=business_user_id).exists():
                    return False
        return True

    def has_object_permission(self, request, view, obj):
        # Nur der Ersteller darf das Review ändern oder löschen
        if request.method in ['PATCH', 'DELETE']:
            return obj.reviewer == request.user
        return True
    

# class IsCustomerAndAuthenticated(permissions.BasePermission):
#     def has_permission(self, request, view):
#         print("User:", request.user)
#         print("Is Authenticated:", request.user.is_authenticated)
#         print("Has Profile:", hasattr(request.user, 'profile'))
#         if hasattr(request.user, 'profile'):
#             print("Is Customer:", request.user.profile.is_customer)
#         return bool(
#             request.user and
#             request.user.is_authenticated and
#             hasattr(request.user, 'profile') and
#             request.user.profile.is_customer
#         )