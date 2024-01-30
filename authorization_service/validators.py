from phonenumbers import parse as parse_phone, is_valid_number
from rest_framework.serializers import ValidationError

class PhoneNumberValidator:
    """ Валидатор для номера телефона """
    def __init__(self):
        pass

    def __call__(self, value):
        try:
            parsed_number = parse_phone(value, None)  # Анализ номера телефона без указания страны
            if not is_valid_number(parsed_number):  # Проверка валидности номера телефона
                raise ValidationError('Неверный номер телефона')
        except Exception as e:
            raise ValidationError('Введите номер телефона в формате +79999999999')
