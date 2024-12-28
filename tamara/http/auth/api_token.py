from tamara.configuration import Configuration


class APITokenAuthentication(object):

    @staticmethod
    def apply(http_request):
        """
        Add token authentication to the header request.
        Args:
            http_request (HttpRequest): The HttpRequest object to which authentication will be added.
        """
        api_token = Configuration.api_token
        header_value = "Bearer {}".format(api_token)
        http_request.headers["Authorization"] = header_value
