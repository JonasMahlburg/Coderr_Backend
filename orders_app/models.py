from django.db import models
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail # Wichtig: Importiere die Offers-Models!

class Order(models.Model):
    # Wer hat bestellt? (Der Kunde)
    # Ein Benutzer kann viele Bestellungen haben
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    # Welches Angebot wurde bestellt?
    # Eine Bestellung bezieht sich auf ein spezifisches Angebot
    # Ein Angebot kann viele Bestellungen haben
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='orders')

    # Welches spezifische Detail des Angebots wurde bestellt?
    # Dies ist wichtig, da ein Offer mehrere OfferDetails haben kann (Basic, Standard, Premium)
    # Eine Bestellung bezieht sich auf ein spezifisches OfferDetail
    # Ein OfferDetail kann viele Bestellungen haben
    # Füge hier related_name='order_items' oder Ähnliches hinzu, wenn du es über OfferDetail abfragen willst
    ordered_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE, related_name='orders_for_detail')

    # Status der Bestellung (z.B. Pending, Accepted, Completed, Cancelled)
    # Du könntest hier auch Choices verwenden
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('in_progress', 'in_Progress'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Menge des bestellten Details (falls man z.B. 2x das "Basic" Paket bestellen kann)
    # Wenn ein Detail immer nur 1x pro Bestellung ist, kannst du dieses Feld weglassen
    quantity = models.PositiveIntegerField(default=1)

    # Der Preis zum Zeitpunkt der Bestellung (um Preisänderungen im OfferDetail abzufangen)
    # Dies ist eine gute Praxis, da sich die Preise eines Offers ändern können,
    # die Bestellung aber den Preis zum Zeitpunkt des Kaufs festhalten sollte.
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)

    # Zeitstempel
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at'] # Neueste Bestellungen zuerst

    def __str__(self):
        return f"Order {self.id} for Offer '{self.offer.title}' (Detail: {self.ordered_detail.title}) by {self.customer.username}"

    # Optional: Eine Methode zur Berechnung des Gesamtpreises der Bestellung
    def get_total_price(self):
        return self.price_at_order * self.quantity