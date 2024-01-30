""" Пагинаторы приложения training_courses """
from rest_framework.pagination import PageNumberPagination


class UserProfilePagination(PageNumberPagination):
    """ Пагинатор для вывода профилей """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50
