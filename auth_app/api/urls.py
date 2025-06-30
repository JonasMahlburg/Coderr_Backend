from django.urls import path
from .views import UserProfileList, UserProfileDetail, RegistrationView, CustomLogInView, BusinessUserListView, CustomerUserListView

urlpatterns = [
    path('profile/', UserProfileList.as_view(), name='userprofile-list'),
    path('profile/<int:pk>/', UserProfileDetail.as_view(), name= 'userprofile-detail'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLogInView.as_view(), name='login'),
    path('profiles/business/', BusinessUserListView.as_view(), name='business-user-list'),
    path('profiles/customer/', CustomerUserListView.as_view(), name='customer-user-list')

]

