import random
import string
from authorization_service.models import UserProfile


def generate_verification_code():
    """ Метод для генерации кода верификации """
    return ''.join(random.choice('0123456789') for _ in range(4))


def send_password_to_user(phone_number, password):
    """ Отправка сообщения с новым паролем на указанный номер телефона """
    pass


def generate_referral_code():
    """Генерация случайного реферального кода в виде строки"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def get_verification_code_from_db(user):
    """ Метод для получения кода верификации из базы данных """
    try:
        profile = UserProfile.objects.get(user=user)
        return profile.verification_code
    except UserProfile.DoesNotExist:
        return None

