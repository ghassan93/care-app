class CheckPaymentOptionsAvailabilityResponse(object):
    """
    Check if there are any available payment options for customer with the given order value
    """

    HAS_AVAILABLE_PAYMENT_OPTIONS = 'has_available_payment_options'

    def __init__(self, has_available_payment_options: str):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """

        self.has_available_payment_options = has_available_payment_options

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {self.HAS_AVAILABLE_PAYMENT_OPTIONS: self.has_available_payment_options}

    @classmethod
    def form_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        has_available_payment_options = dictionary.get(cls.HAS_AVAILABLE_PAYMENT_OPTIONS)

        # Return an object of this model
        return cls(has_available_payment_options=has_available_payment_options)
