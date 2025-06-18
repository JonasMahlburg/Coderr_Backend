# orders_app/views.py
from rest_framework import generics
from orders_app.models import Order
from .serializers import OrderCombinedSerializer # Importiere den neuen Serializer
from rest_framework.permissions import IsAuthenticated


class OrderListCreateView(generics.ListCreateAPIView):
    # Das Queryset sollte alle Orders enthalten, auf die der Benutzer zugreifen darf
    # Hier ein Beispiel, dass nur die Orders des eingeloggten Customers oder Business User anzeigt
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Zeigt Orders, wo der User der Kunde ist ODER wo der User der Business-User des Offers ist
            return Order.objects.filter(customer=user).distinct() | \
                   Order.objects.filter(offer__user=user).distinct()
        return Order.objects.none() # Keine Orders für unauthentifizierte User

    # Verwende den OrderCombinedSerializer für GET-Anfragen (List view)
    def get_serializer_class(self):
        # Wenn du nur diesen kombinierten Serializer für GET nutzen willst:
        if self.request.method == 'GET':
            return OrderCombinedSerializer
        # Für POST-Anfragen zur Erstellung einer Bestellung, brauchst du weiterhin einen Serializer,
        # der Schreiboperationen unterstützt (z.B. den OrderSerializer, den wir zuvor hatten).
        # Wenn du nur die GET-Funktionalität des kombinierten Serializers brauchst,
        # dann musst du hier den Serializer für POST definieren (z.B. OrderSerializer)
        from .serializers import OrderSerializer # Gehe davon aus, dass du den OrderSerializer für POST nutzt
        return OrderSerializer


    permission_classes = [IsAuthenticated] # Der Benutzer muss angemeldet sein


    def perform_create(self, serializer):
        # Setze den Kunden automatisch auf den aktuell eingeloggten Benutzer
        serializer.save(customer=self.request.user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Das Queryset sollte alle Orders enthalten, auf die der Benutzer zugreifen darf
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Nur die eigene Order oder eine Order, bei der der User der Business-User des Offers ist
            return Order.objects.filter(pk=self.kwargs['pk']).filter(customer=user) | \
                   Order.objects.filter(pk=self.kwargs['pk']).filter(offer__user=user)
        return Order.objects.none()

    # Verwende den OrderCombinedSerializer für GET-Anfragen (Detail view)
    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderCombinedSerializer
        # Für PUT/PATCH brauchst du einen Serializer, der Schreiboperationen unterstützt.
        # Hier könntest du z.B. den ursprünglichen OrderSerializer oder einen spezifischen OrderPatchSerializer verwenden,
        # je nachdem, wie du die Aktualisierung der Bestellungen handhaben möchtest.
        from .serializers import OrderSerializer # Oder OrderPatchSerializer
        return OrderSerializer

    permission_classes = [IsAuthenticated]
    lookup_field = 'pk' # Stellen wir sicher, dass es 'pk' ist, wie in urls.py definiert