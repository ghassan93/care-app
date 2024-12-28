class AuthoriseOrderRequest(object):
    """
    Merchant will be required to call to Authorize API the order after receiving the notification from Tamara
    about the order being ‘Approved’.
    This is one of the most important flows the merchant needs to complete.
    """

    ORDER_ID = 'order_id'

    def __init__(self, order_id: str):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.order_id = order_id

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {self.ORDER_ID: self.order_id}

    @classmethod
    def form_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        order_id = dictionary.get(cls.ORDER_ID)

        # Return an object of this model
        return cls(order_id=order_id)
