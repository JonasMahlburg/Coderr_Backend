from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, OfferDetailViewSet

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'offerdetails', OfferDetailViewSet, basename='offerdetail')

urlpatterns = router.urls

