# offers_app/urls.py

from django.urls import path
from .views import OfferListCreateView, OfferDetailView, OfferDetailRetrieveView

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offer-list'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-create'),
    path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(), name='offer-detail' )

]

