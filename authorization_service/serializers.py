from rest_framework import serializers
from authorization_service.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для модели UserProfile"""
    referred_by = serializers.SerializerMethodField()
    referred_users = serializers.SerializerMethodField()

    def get_referred_by(self, obj):
        if obj.referrer:
            return obj.referrer.username
        else:
            return None

    def get_referred_users(self, obj):
        user_referral_code = obj.user_referral_code
        if user_referral_code:
            referred_users = UserProfile.objects.filter(activated_referral_code=user_referral_code).exclude(user=obj.user)
            if referred_users.exists():
                return [user.user.username for user in referred_users]
        return None

    class Meta:
        """Мета-данные"""
        model = UserProfile
        fields = ['id', 'phone_number', 'user_referral_code', 'user_referred_code_used', 'referred_users', 'activated_referral_code', 'referred_by']

