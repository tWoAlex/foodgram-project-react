from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = settings.REST_FRAMEWORK.get('PAGELIMITPAGINATION_PAGE_SIZE', 6)
