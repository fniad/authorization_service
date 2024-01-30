""" Модели приложения users """
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Модель пользователя """
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username}"

    class Meta:
        """ Мета-данные """
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
