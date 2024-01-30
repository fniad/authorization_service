""" Тесты для authorization_service """
import pytest
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from authorization_service.models import UserProfile
from users.models import User


@pytest.fixture
def user_first():
    """ Кэшируемая фикстура для создания первого пользователя """
    return User.objects.create_user(
        username='+79996691554',
        password='1234'
    )


@pytest.fixture
def api_client():
    """ Фикстура для создания API клиента """
    return APIClient()


@pytest.fixture
def jwt_token_for_first_user(user_first):
    """ Фикстура для создания JWT токена """
    token = AccessToken.for_user(user_first)
    return f'Bearer {token}'


@pytest.fixture
def user_second():
    """ Фикстура для создания второго пользователя """
    return User.objects.create_user(
        username='+79999999999',
        password='1234'
    )


@pytest.fixture
def first_user_profile(user_first):
    """ Фикстура для создания первого верифицированного профиля """
    return UserProfile.objects.create(
        user=user_first,
        phone_number=user_first.username,
        verification_code='5432',
        activated_referral_code=None,
        user_referral_code='OPT65L4',
        user_referred_code_used=False,
        referrer=None
    )


@pytest.fixture
def second_user_profile(user_second):
    """ Фикстура для создания второго верифицированного профиля """
    return UserProfile.objects.create(
        user=user_second,
        phone_number=user_second.username,
        verification_code='5925',
        activated_referral_code=None,
        user_referral_code='WRT52L',
        user_referred_code_used=False,
        referrer=None
    )


@pytest.fixture
def incorrect_phone_number():
    """ Фикстура некорректного номера телефона """
    return '8712831'


@pytest.fixture
def correct_verification_code(first_user_profile):
    """ Фикстура корректного кода верификации """
    return first_user_profile.verification_code


@pytest.fixture
def incorrect_verification_code():
    """ Фикстура некорректного кода верификации """
    return '1234'


# Тесты для входа в аккаунт и получения кода верификации

@pytest.mark.django_db
def test_user_login_api(client, user_first, first_user_profile):
    """ Тест для входа в аккаунт и получения кода верификации по СМС"""
    data = {'phone_number': user_first.username}
    response = client.post('/user-login/', data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_new_user_login_api(client):
    """ Тест для входа нового пользователя в аккаунт и получения кода верификации по СМС"""
    data = {'phone_number': '+79999999991'}
    response = client.post('/user-login/', data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_incorrect_phone_number_api(client, incorrect_phone_number):
    """ Тест для входа по некорректному номеру телефона """
    data = {'phone_number': incorrect_phone_number}
    response = client.post('/user-login/', data)
    assert response.status_code == 400
    assert response.data == [ErrorDetail(string='Введите номер телефона в формате +79999999999', code='invalid')]


@pytest.mark.django_db
def test_input_correct_verification_code_api(client, user_first, correct_verification_code):
    """ Тест для ввода кода верификации """
    data = {'phone_number': user_first.username, 'entered_code': correct_verification_code}
    response = client.post('/input_verification_code/', data)
    assert response.status_code == 200
    assert response.data['message'] == 'Вход выполнен успешно'


@pytest.mark.django_db
def test_input_incorrect_verification_code_api(client, user_first, incorrect_verification_code):
    """ Тест для ввода некорректного кода верификации """
    data = {'phone_number': user_first.username, 'entered_code': incorrect_verification_code}
    response = client.post('/input_verification_code/', data)
    assert response.status_code == 400
    assert response.data['error'] == 'Отсутствует код верификации'


@pytest.mark.django_db
def test_input_incorrect_phone_number_to_verification_code_api(client, incorrect_phone_number,
                                                               correct_verification_code):
    """ Тест для ввода некорректного телефона при проверке кода верификации """
    data = {'phone_number': incorrect_phone_number, 'entered_code': correct_verification_code}
    response = client.post('/input_verification_code/', data)
    assert response.status_code == 400
    assert response.data == [ErrorDetail(string='Введите номер телефона в формате +79999999999', code='invalid')]


# Тесты для работы с профилями

@pytest.mark.django_db
def test_list_user_profiles_api(client, user_first, first_user_profile, user_second, second_user_profile):
    """ Тест для получения списка профилей """
    response = client.get('/userprofiles/')
    assert response.status_code == 200
    profiles_data = response.json()
    assert profiles_data == {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": first_user_profile.id,
                "phone_number": first_user_profile.phone_number,
                "user_referral_code": first_user_profile.user_referral_code,
                "user_referred_code_used": first_user_profile.user_referred_code_used,
                "referred_users": None,
                "activated_referral_code": first_user_profile.activated_referral_code,
                "referred_by": None
            },
            {
                "id": second_user_profile.id,
                "phone_number": second_user_profile.phone_number,
                "user_referral_code": second_user_profile.user_referral_code,
                "user_referred_code_used": second_user_profile.user_referred_code_used,
                "referred_users": None,
                "activated_referral_code": second_user_profile.activated_referral_code,
                "referred_by": None
            }
        ]
    }


@pytest.mark.django_db
def test_get_user_profile_api(api_client, user_first, first_user_profile, jwt_token_for_first_user):
    """ Тест для получения профиля пользователя """
    api_client.force_authenticate(user=user_first)
    response = api_client.get(f'/userprofiles/{first_user_profile.id}/')
    assert response.status_code == 200
    profile_data = response.json()
    assert profile_data == {
        "id": first_user_profile.id,
        "phone_number": first_user_profile.phone_number,
        "user_referral_code": first_user_profile.user_referral_code,
        "user_referred_code_used": first_user_profile.user_referred_code_used,
        "referred_users": None,
        "activated_referral_code": first_user_profile.activated_referral_code,
        "referred_by": None
    }


@pytest.mark.django_db
def test_update_self_user_profile_api(api_client, user_first, first_user_profile, second_user_profile,
                                      jwt_token_for_first_user):
    """ Тест для ввода реферального кода другого пользователя в профиле пользователя """
    data = {'referral_code': second_user_profile.user_referral_code}
    api_client.force_authenticate(user=user_first)
    response = api_client.put(f'/userprofiles/{first_user_profile.id}/', data)
    assert response.status_code == 200
    assert response.data['message'] == "Вы успешно стали рефералом"


@pytest.mark.django_db
def test_update_self_user_profile_with_incorrect_referral_code_api(api_client, user_first, first_user_profile,
                                                                  jwt_token_for_first_user):
    """ Тест для ввода неверного реферального кода в профиле пользователя """
    data = {'referral_code': 'O89G61'}
    api_client.force_authenticate(user=user_first)
    response = api_client.put(f'/userprofiles/{first_user_profile.id}/', data)
    assert response.status_code == 400
    assert response.data['error'] == "Неверный реферальный код"


@pytest.mark.django_db
def test_update_other_user_profile_api(api_client, user_first, user_second, first_user_profile, second_user_profile,
                                       jwt_token_for_first_user):
    """ Тест для ввода реферального кода другого пользователя в профиле другого пользователя """
    data = {'referral_code': second_user_profile.user_referral_code}
    api_client.force_authenticate(user=user_first)
    response = api_client.put(f'/userprofiles/{second_user_profile.id}/', data)
    assert response.status_code == 403
    assert response.data['detail'] == 'Вы не можете изменять и просматривать чужие профили'


@pytest.mark.django_db
def test_update_self_user_profile_with_self_referral_code_api(api_client, user_first, first_user_profile,
                                                              jwt_token_for_first_user):
    """ Тест для ввода реферального кода самого себя в профиле пользователя """
    data = {'referral_code': first_user_profile.user_referral_code}
    api_client.force_authenticate(user=user_first)
    response = api_client.put(f'/userprofiles/{first_user_profile.id}/', data)
    assert response.status_code == 400
    assert response.data['error'] == 'Вы не можете использовать свой собственный реферальный код'


@pytest.mark.django_db
def test_delete_user_profile_api(api_client, user_first, first_user_profile, jwt_token_for_first_user):
    """ Тест для удаления профиля пользователя """
    api_client.force_authenticate(user=user_first)
    response = api_client.delete(f'/userprofiles/{first_user_profile.id}/')
    assert response.status_code == 403
    assert response.data['detail'] == 'У вас недостаточно прав для выполнения данного действия.'


@pytest.mark.django_db
def test_delete_other_user_profile_api(api_client, user_first, user_second, second_user_profile,
                                       jwt_token_for_first_user):
    """ Тест для удаления профиля другого пользователя """
    api_client.force_authenticate(user=user_first)
    response = api_client.delete(f'/userprofiles/{second_user_profile.id}/')
    assert response.status_code == 403
    assert response.data['detail'] == 'У вас недостаточно прав для выполнения данного действия.'


@pytest.mark.django_db
def test_create_user_profile_api(api_client, user_first, jwt_token_for_first_user):
    """ Тест для создания профиля пользователя """
    data = {'phone_number': '88005553535'}
    api_client.force_authenticate(user=user_first)
    response = api_client.post('/userprofiles/', data)
    assert response.status_code == 403
    assert response.data['detail'] == 'У вас недостаточно прав для выполнения данного действия.'
