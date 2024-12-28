import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from tamara.http.http_client import HttpClient
from tamara.http.http_method_enum import HttpMethodEnum
from tamara.http.http_response import HttpResponse


class RequestsClient(HttpClient):
    """
    An implementation of HttpClient that uses Requests as its HTTP Client
    """

    def __init__(self, timeout=60, cache=False, max_retries=None, retry_interval=None):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.timeout = timeout
        self.session = requests.session()

        if max_retries and retry_interval:
            retries = Retry(total=max_retries, backoff_factor=retry_interval)
            self.session.mount('http://', HTTPAdapter(max_retries=retries))
            self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def execute(self, request):
        """
        Execute a given HttpRequest to get a string response back
        """

        response = self.session.request(
            HttpMethodEnum.to_string(request.http_method),
            request.query_url,
            headers=request.headers,
            params=request.query_parameters,
            data=request.parameters,
            files=request.files,
            timeout=self.timeout
        )

        return self.convert_response(response)

    def convert_response(self, response):
        """
        Converts the Response object of the HttpClient into an
        HttpResponse object.
        """
        return HttpResponse(response.status_code, response.headers, response.text)
