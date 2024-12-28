class HttpMethodEnum(object):
    """
    Enumeration of an HTTP Method
    """

    GET = "GET"

    POST = "POST"

    PUT = "PUT"

    PATCH = "PATCH"

    DELETE = "DELETE"

    HEAD = "HEAD"

    @classmethod
    def to_string(cls, val):
        """Returns the string equivalent for the Enum.

        """
        for k, v in list(vars(cls).items()):
            if v == val:
                return k

    @classmethod
    def from_string(cls, str):
        """Creates an instance of the Enum from a given string.

        """
        return getattr(cls, str.upper(), None)
