class APIException(Exception):
    """
    Class that handles HTTP Exceptions when fetching API Endpoints.
    """

    def __init__(self, message, context):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(APIException, self).__init__(message)
        self.context = context
        self.response_code = context.response.status_code
