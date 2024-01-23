from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    """ Модель профиля пользователя """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=16, unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.phone_number}"

    class Meta:
        """ Мета-данные """
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'профили пользователей'


class ReferralCode(models.Model):
    """ Модель реферального кода """
    code = models.CharField(max_length=6, unique=True)
    referrer = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='referral_code')

    def __str__(self):
        return self.code

    class Meta:
        """ Мета-данные """
        verbose_name = 'реферальный код'
        verbose_name_plural = 'реферальные коды'


class Referral(models.Model):
    """ Модель рефералов """
    referring_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='referrals')
    referral_code = models.ForeignKey(ReferralCode, on_delete=models.SET_NULL, null=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    created_at = models.DateTimeField(auto_now_add=True)
    referred_code_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Referral: {self.referral_code.code}, Referrer: {self.referring_user.user.username}"

    def mark_referred_code_used(self):
        """ Метод для отметки использования инвайта """
        self.referred_code_used = True
        self.save()

    class Meta:
        """ Мета-данные """
        verbose_name = 'реферал'
        verbose_name_plural = 'рефералы'
