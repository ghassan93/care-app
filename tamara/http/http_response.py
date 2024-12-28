

class HttpResponse(object):
    """
    Information about an HTTP Response including its status code, returned
    headers, and raw body
    """

    def __init__(self, status_code, headers, raw_body):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.status_code = status_code
        self.headers = headers
        self.raw_body = raw_body
