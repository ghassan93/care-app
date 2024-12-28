from tamara.models.order.order import Order


class CreateCheckoutSessionRequest(object):
    """
    Create a checkout session and pass through all the payment information in the request.
    The response will have order_id, checkout_id and checkout_url.
    Please retain the order_id to fetch the information about the order later
    and redirect the customer to checkout_url to complete the transaction via Tamara.
    """

    ORDER = 'order'

    def __init__(self, order: Order):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.order = order

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return self.order.to_dictionary()

    @classmethod
    def form_dictionary(cls, order: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if order is None:
            return None

        # Extract variables from the dictionary
        order = Order.from_dictionary(order)

        # Return an object of this model
        return cls(order=order)
