class CreateCheckoutSessionResponse(object):
    """
    Create a checkout session and pass through all the payment information in the request.
    The response will have order_id, checkout_id and checkout_url.
    Please retain the order_id to fetch the information about the order later
    and redirect the customer to checkout_url to complete the transaction via Tamara.
    """

    ORDER_ID = 'order_id'
    CHECKOUT_ID = 'checkout_id'
    CHECKOUT_URL = 'checkout_url'

    def __init__(self, order_id: str, checkout_id: str, checkout_url: str):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """

        self.order_id = order_id
        self.checkout_id = checkout_id
        self.checkout_url = checkout_url

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.ORDER_ID: self.order_id,
            self.CHECKOUT_ID: self.checkout_id,
            self.CHECKOUT_URL: self.checkout_url,
        }

    @classmethod
    def form_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        order_id = dictionary.get(cls.ORDER_ID)
        checkout_id = dictionary.get(cls.CHECKOUT_ID)
        checkout_url = dictionary.get(cls.CHECKOUT_URL)

        # Return an object of this model
        return cls(order_id=order_id, checkout_id=checkout_id, checkout_url=checkout_url)
