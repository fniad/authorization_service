""" Представления для users """
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from users.models import User
from users.pagination import UserPagination
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ ViewSet для пользователей """
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('pk')
    permission_classes = [IsAdminUser]
    pagination_class = UserPagination
