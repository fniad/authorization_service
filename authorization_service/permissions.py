""" Права доступа в приложении authorization_service """
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """ Только для текущего пользователя """
    message = 'Вы не можете изменять и просматривать чужие профили'
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
