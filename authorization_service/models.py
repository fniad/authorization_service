from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    """ Модель профиля пользователя """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=16, unique=True)
    verification_code = models.CharField(max_length=4)
    activated_referral_code = models.CharField(max_length=8, null=True, default=None)
    user_referral_code = models.CharField(max_length=8, unique=True)
    user_referred_code_used = models.BooleanField(default=False)
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referrals',
                                 null=True)

    def __str__(self):
        return f"{self.user}"

    def mark_user_referred_code_used(self):
        """ Метод для отметки использования инвайта """
        self.referred_code_used = True
        self.save()

    class Meta:
        """ Мета-данные """
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'профили пользователей'
