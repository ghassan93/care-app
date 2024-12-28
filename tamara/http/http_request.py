from tamara.helpers.api_helper import APIHelper


class HttpRequest(object):
    """
    Information about an HTTP Request including its method, headers,
    parameters, URL, and Basic Auth details
    """

    def __init__(self, http_method, query_url, headers=None, query_parameters=None, parameters=None, files=None):
        """
        Constructor for the HttpRequest class
        """
        self.http_method = http_method
        self.query_url = query_url
        self.headers = headers
        self.query_parameters = query_parameters
        self.parameters = parameters
        self.files = files

    def add_header(self, name, value):
        """
        Add a header to the HttpRequest.
        """
        self.headers[name] = value

    def add_parameter(self, name, value):
        """
        Add a parameter to the HttpRequest.
        """
        self.parameters[name] = value

    def add_query_parameter(self, name, value):
        """
        Add a query parameter to the HttpRequest.
        """
        self.query_url = APIHelper.append_url_with_query_parameters(self.query_url,
                                                                    {name: value})
        self.query_url = APIHelper.clean_url(self.query_url)
