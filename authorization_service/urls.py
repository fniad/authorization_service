from django.urls import path
from rest_framework.routers import DefaultRouter

from authorization_service.apps import AuthorizationServiceConfig
from authorization_service.views import UserProfileLoginAPI, \
    InputVerificationCodeAPI, UserProfileViewSet

app_name = AuthorizationServiceConfig.name
router = DefaultRouter()
router.register(r'userprofiles', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('user_login/', UserProfileLoginAPI.as_view(), name='user_login'),
    path('input_verification_code/', InputVerificationCodeAPI.as_view(), name='input_verification_code'),
] + router.urls
