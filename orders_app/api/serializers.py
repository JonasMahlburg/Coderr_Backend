from rest_framework import serializers
from orders_app.models import Order # Importiere das Order-Modell
from offers_app.models import Offer, OfferDetail # Importiere die relevanten Offers-Modelle
from offers_app.api.serializers import OfferDetailSerializer, OfferSerializer # Importiere deine bestehenden Serializer
from django.contrib.auth.models import User

# Optional: Ein einfacher Serializer für den User, falls du detaillierte User-Infos brauchst
class UserSerializerForOrder(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name'] # Wähle die Felder, die du anzeigen möchtest

class OrderSerializer(serializers.ModelSerializer):
    # Felder für die lesbare Darstellung (GET-Requests)

    # Zeige detaillierte Informationen über den Kunden
    # `read_only=True` da der Kunde über den Token des eingeloggten Users gesetzt wird
    customer = UserSerializerForOrder(read_only=True)

    # Zeige detaillierte Informationen über das bestellte Offer
    # `read_only=True` für GET-Requests. Beim Erstellen wird nur die Offer-ID erwartet.
    # Du könntest auch einen einfacheren Offer-Serializer hier verwenden, der nur id und title hat.
    # Für den Moment nehmen wir den vollen OfferSerializer, aber mit read_only=True.
    offer = OfferSerializer(read_only=True)

    # Zeige detaillierte Informationen über das bestellte OfferDetail
    # `read_only=True` für GET-Requests. Beim Erstellen wird nur die OfferDetail-ID erwartet.
    ordered_detail = OfferDetailSerializer(read_only=True)

    # Zusätzliche berechnete Felder (optional, falls du sie nicht im Model hast)
    # Wenn price_at_order im Model ist, brauchst du dieses get_total_price nicht mehr als SerializerMethodField.
    # get_total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'offer', 'ordered_detail', 'status',
            'quantity', 'price_at_order', 'created_at', 'updated_at'
            # Füge hier get_total_price hinzu, wenn du es als SerializerMethodField nutzen willst
        ]
        read_only_fields = ['customer', 'created_at', 'updated_at', 'price_at_order'] # Diese Felder sollten nicht vom Client gesetzt werden

    # Custom create-Methode für verschachteltes Schreiben
    # Beim Erstellen einer Bestellung (POST) sendest du nur die IDs
    # Für PATCH/PUT musst du überlegen, ob du diese Felder direkt ändern lassen willst
    def create(self, validated_data):
        # Wir müssen die IDs für Offer und OfferDetail manuell behandeln,
        # da sie nicht direkt als Objekte im validated_data sind, wenn sie nur als IDs gesendet werden.
        # Aber da wir sie als read_only=True im Serializer definiert haben, sind sie nicht in validated_data.
        # Stattdessen wird die View die FK-Objekte direkt setzen.

        # Hier ist ein Beispiel, wie man die ForeignKey-Objekte setzen würde,
        # wenn sie als ID im validated_data kämen und nicht direkt von der View gesetzt würden.
        # Da wir sie read-only für die Ausgabe haben, werden wir erwarten, dass die View sie setzt.

        # Für die Erstellung ist es oft so, dass der Kunde, das Angebot und das Detail
        # als IDs im Request-Body gesendet werden. Der Serializer muss das verarbeiten können.
        # Dazu müssen wir die Felder im Serializer anders definieren, wenn sie beschreibbar sein sollen.

        # Da du bereits `customer = UserSerializerForOrder(read_only=True)` hast,
        # gehst du davon aus, dass `customer` vom Request User gesetzt wird.
        # Für `offer` und `ordered_detail` müsstest du `PrimaryKeyRelatedField` nutzen.

        # Neudefinition der Felder für das Schreiben
        # Diese Create-Methode muss angepasst werden, wenn du die `offer` und `ordered_detail` IDs direkt in deinem POST-Payload haben möchtest.
        # Standardmäßig, wenn du `ForeignKey` in ModelSerializer nicht explizit als `PrimaryKeyRelatedField` definierst,
        # erwartet er die ID.
        return super().create(validated_data)

    # def get_total_price(self, obj):
    #     return obj.get_total_price() # Ruft die Methode aus dem Order-Modell auf

    # Validierung, falls nötig (z.B. um sicherzustellen, dass ordered_detail auch wirklich zum offer gehört)
    def validate(self, data):
        if 'offer' in data and 'ordered_detail' in data:
            offer = data['offer']
            ordered_detail = data['ordered_detail']
            if ordered_detail.offer != offer:
                raise serializers.ValidationError(
                    {"ordered_detail": "Das ausgewählte Detail gehört nicht zum angegebenen Angebot."}
                )
        return data
    

class OrderCombinedSerializer(serializers.ModelSerializer):
    # Felder aus dem OfferDetail-Modell, die direkt auf die Order-Ebene gehoben werden
    title = serializers.CharField(source='ordered_detail.title', read_only=True)
    revisions = serializers.IntegerField(source='ordered_detail.revisions', read_only=True)
    delivery_time_in_days = serializers.IntegerField(source='ordered_detail.delivery_time_in_days', read_only=True)
    price = serializers.DecimalField(source='ordered_detail.price', max_digits=10, decimal_places=2, read_only=True)
    features = serializers.JSONField(source='ordered_detail.features', read_only=True)
    offer_type = serializers.CharField(source='ordered_detail.offer_type', read_only=True)

    # Felder, die den Benutzer (Kunden) und den Business-Benutzer (Anbieter) referenzieren
    # customer_user: ID des Benutzers, der die Bestellung aufgegeben hat
    customer_user = serializers.PrimaryKeyRelatedField(source='customer', read_only=True)

    # business_user: ID des Benutzers, dem das bestellte Angebot gehört
    # Wir müssen durch das 'offer'-Feld der Order zum 'user'-Feld des Offers navigieren
    business_user = serializers.PrimaryKeyRelatedField(source='offer.user', read_only=True)


    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title', # Von OfferDetail
            'revisions', # Von OfferDetail
            'delivery_time_in_days', # Von OfferDetail
            'price', # Von OfferDetail
            'features', # Von OfferDetail
            'offer_type', # Von OfferDetail
            'status', # Vom Order-Modell
            'created_at', # Vom Order-Modell
            'updated_at' # Vom Order-Modell
        ]
        # Alle Felder in diesem Serializer sollen nur gelesen werden können für diese kombinierte Ansicht
        read_only_fields = fields