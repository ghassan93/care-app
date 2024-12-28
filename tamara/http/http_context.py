class HttpContext(object):
    """
    An HTTP Context that contains both the original HttpRequest
    object that initiated the call and the HttpResponse object that
    is the result of the call.
    """

    def __init__(self, request, response):
        """
        Constructor for the HttpContext class
        """
        self.request = request
        self.response = response
