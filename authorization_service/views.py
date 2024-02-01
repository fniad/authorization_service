""" Представления для сервиса authorization_service"""
import time

from django.core.validators import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import (IsAuthenticated, AllowAny,
                                        IsAdminUser, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authorization_service.models import UserProfile
from authorization_service.pagination import UserProfilePagination
from authorization_service.permissions import IsOwner
from authorization_service.serializers import UserProfileSerializer
from authorization_service.utils import generate_verification_code, get_verification_code_from_db, \
    send_password_to_user, generate_referral_code
from authorization_service.validators import PhoneNumberValidator
from users.models import User


class UserProfileLoginAPI(APIView):
    """ Представление для входа в аккаунт и получения кода верификации
    params: {'phone_number': '+79999999999'}"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING,
                                               description='Номер телефона в формате +79999999999'),
            }
        ),
        responses={200: 'OK', 400: 'Invalid Request'},
        operation_description='Представление для входа в аккаунт и получения кода верификации'
    )
    def post(self, request):
        """ Представление для входа в аккаунт и получения кода верификации """
        phone_number = request.data.get('phone_number')

        try:
            phone_number_validator = PhoneNumberValidator()
            phone_number_validator(phone_number)
        except DjangoValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        verification_code = generate_verification_code()

        try:
            user = User.objects.get(username=phone_number)
            profile = UserProfile.objects.get(user=user)
            profile.verification_code = verification_code
            profile.save()
            print(f'Код верификации для номера {phone_number}: {verification_code}')
        except User.DoesNotExist:

            password = get_random_string(6)
            print(f'Пароль для номера {phone_number}: {password}')
            send_password_to_user(phone_number, password)  # Отправка сообщения о новом пароле

            user = User.objects.create_user(username=phone_number, password=password)
            referral_code = generate_referral_code()
            profile = UserProfile.objects.create(
                user=user,
                phone_number=phone_number,
                verification_code=verification_code,
                user_referral_code=referral_code
            )
            profile.refresh_from_db()
            print(f'Код верификации для номера {phone_number}: {verification_code}')

        return Response({'message': 'Введите верификационный код из СМС для входа POST /input_verification_code/'})


class InputVerificationCodeAPI(APIView):
    """ Представление для ввода кода верификации
    params: {'phone_number': '+79999999999', 'entered_code': '1234'}"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING,
                                               description='Номер телефона в формате +79999999999'),
                'entered_code': openapi.Schema(type=openapi.TYPE_STRING,
                                               description='Код верификации, полученный по СМС')
            }
        ),
        responses={200: 'OK', 400: 'Invalid Request'},
        operation_description='Представление для ввода кода верификации'
    )
    def post(self, request):
        """ Представление для ввода кода верификации """
        time.sleep(2)
        username = request.data.get('phone_number')

        try:
            phone_number_validator = PhoneNumberValidator()
            phone_number_validator(username)
        except DjangoValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_400_BAD_REQUEST)

        entered_code = request.data.get('entered_code')
        if entered_code == '':
            return Response({'error': 'Отсутствует код верификации'}, status=status.HTTP_400_BAD_REQUEST)

        verification_code = get_verification_code_from_db(user=user)
        if entered_code == verification_code:
            user_profile = UserProfile.objects.filter(user=user).first()
            if user_profile:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                return Response({'access_token': access_token, 'message': 'Вход выполнен успешно'})
            raise NotFound("Профиль пользователя не найден")
        return Response({'error': 'Неверный код верификации'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ Представление для работы с профилями пользователей """
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all().order_by('id')
    pagination_class = UserProfilePagination

    def get_object_or_none(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {'id': self.kwargs['pk']}
        try:
            obj = queryset.get(**filter_kwargs)
            if not self.request.user == obj.user:
                return None
            return obj
        except UserProfile.DoesNotExist:
            return None

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'referral_code': openapi.Schema(type=openapi.TYPE_STRING, description='Реферальный код')
            }
        ),
        responses={200: 'OK', 400: 'Invalid Request'},
        operation_description='Обновление профиля пользователя'
    )
    def update(self, request, *args, **kwargs):
        """Обновление профиля пользователя"""
        referral_code = request.data.get('referral_code')
        if referral_code:
            return self._handle_referral_code_update(request, referral_code, *args, **kwargs)
        else:
            return super().update(request, *args, **kwargs)

    def _handle_referral_code_update(self, request, referral_code, *args, **kwargs):
        """Обработка обновления профиля пользователя с реферальным кодом"""
        profile_2 = self.get_object_or_none()
        profile = self.get_object()
        if profile_2 is None:
            return Response({'error': 'Профиль с таким реферальным кодом не найден'}, status=status.HTTP_404_NOT_FOUND)

        if referral_code == profile.user_referral_code:
            return Response({'error': 'Вы не можете использовать свой собственный реферальный код'},
                            status=status.HTTP_400_BAD_REQUEST)

        if profile.activated_referral_code == referral_code:
            return Response({'error': 'Вы уже активировали этот реферальный код'},
                            status=status.HTTP_400_BAD_REQUEST)

        referred_by = get_object_or_404(UserProfile, user_referral_code=referral_code)

        if profile.activated_referral_code and profile.activated_referral_code != referral_code:
            return Response({'error': 'У вас уже активирован другой реферальный код'},
                            status=status.HTTP_400_BAD_REQUEST)

        self._process_referral_code_update(profile, referred_by, referral_code)

        profile.referrer = referred_by.user
        profile.save()

        return Response({'message': 'Вы успешно стали рефералом'}, status=status.HTTP_200_OK)

    def _process_referral_code_update(self, profile, referred_by, referral_code):
        """Обработка успешного обновления профиля с реферальным кодом"""
        if not profile.activated_referral_code:
            profile.activated_referral_code = referral_code
            profile.referrer = referred_by.user
            profile.save()
            referred_by.user_referred_code_used = True
            referred_by.save()
        else:
            return Response({'error': 'У вас уже активирован реферальный код'},
                            status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        """ Права доступа для работы с профилями пользователей"""
        if self.action in ['create', 'destroy', 'partial_update']:
            self.permission_classes = [IsAdminUser]
        elif self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        elif self.action in ['update']:
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return super().get_permissions()
