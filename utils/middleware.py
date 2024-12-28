from django.middleware.locale import LocaleMiddleware as DjangoLocaleMiddleware


class LocaleMiddleware(DjangoLocaleMiddleware):

    def process_request(self, request):
        request.META['HTTP_ACCEPT_LANGUAGE'] = ''
        super(LocaleMiddleware, self).process_request(request)
