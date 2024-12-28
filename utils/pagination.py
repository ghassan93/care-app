import math

from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'start'
    page_size_query_param = 'length'
    max_page_size = 100

    def get_custom_page_number(self, request, paginator, page_size):
        page_number = request.query_params.get(self.page_query_param, 0)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        if int(page_number) < page_size:
            return 1
        return abs(math.ceil((int(page_number) - 1) / page_size)) + 1

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)

        if not page_size:
            return None

        if page_size < 0:
            page_size = queryset.count() or 10

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_custom_page_number(request, paginator, page_size)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_paginated_response(self, data):
        return Response(dict(page=self.page.number, recordsTotal=self.page.paginator.count,
                             recordsFiltered=self.page.paginator.count, data=data))


def _positive_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    """
    ret = int(integer_string)
    if ret == 0 and strict:
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret
