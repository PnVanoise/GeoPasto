from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class DefaultPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        # Extend default paginated response with page_size so clients can
        # compute total pages reliably
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page.paginator.per_page,
            'results': data,
        })
