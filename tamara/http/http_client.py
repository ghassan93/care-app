from tamara.http.http_method_enum import HttpMethodEnum
from tamara.http.http_request import HttpRequest


class HttpClient(object):
    """
    An interface for the methods that an HTTP Client must implement
    This class should not be instantiated but should be used as a base class
    for HTTP Client classes.
    """

    def execute(self, request):
        """
        Execute a given HttpRequest to get a string response back
        """
        raise NotImplementedError("Please Implement this method")

    def convert_response(self, response, binary):
        """
        Converts the Response object of the HttpClient into an
        HttpResponse object.
        """
        raise NotImplementedError("Please Implement this method")

    def get(self, query_url, headers=None, query_parameters=None):
        """
        Create a simple GET HttpRequest object for the given parameters
        """

        return HttpRequest(HttpMethodEnum.GET, query_url, headers, query_parameters, None, None)

    def head(self, query_url, headers=None, query_parameters=None):
        """
        Create a simple HEAD HttpRequest object for the given parameters
        """
        return HttpRequest(HttpMethodEnum.HEAD, query_url, headers, query_parameters, None, None)

    def post(self, query_url, headers=None, query_parameters=None, parameters=None, files=None):
        """
        Create a simple POST HttpRequest object for the given parameters
        """
        return HttpRequest(HttpMethodEnum.POST, query_url, headers, query_parameters, parameters, files)

    def put(self, query_url, headers=None, query_parameters=None, parameters=None, files=None):
        """
        Create a simple PUT HttpRequest object for the given parameters
        """
        return HttpRequest(HttpMethodEnum.PUT, query_url, headers, query_parameters, parameters, files)

    def patch(self, query_url, headers=None, query_parameters=None, parameters=None, files=None):
        """
        Create a simple PATCH HttpRequest object for the given parameters
        """
        return HttpRequest(HttpMethodEnum.PATCH, query_url, headers, query_parameters, parameters, files)

    def delete(self, query_url, headers=None, query_parameters=None, parameters=None, files=None):
        """
        Create a simple DELETE HttpRequest object for the given parameters
        """
        return HttpRequest(HttpMethodEnum.DELETE, query_url, headers, query_parameters, parameters, files)
