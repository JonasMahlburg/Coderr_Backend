"""
Custom pagination settings for paginated offer result views in the offers_app.
"""

from rest_framework.pagination import PageNumberPagination

class OffersResultPagination(PageNumberPagination):
    """
    Pagination class for offers, allowing a default page size of 6 and
    supporting a 'page_size' query parameter with a maximum limit.
    """
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'