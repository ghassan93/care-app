class CaptureResponse(object):
    """
    Merchants can partially or fully capture an order after the order is shipped to the customer
    depending on partial shipment or full shipment.
    """

    CAPTURE_ID = 'capture_id'
    ORDER_ID = 'order_id'

    def __init__(self, capture_id: str = None, order_id: str = None):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """

        self.capture_id = capture_id
        self.order_id = order_id

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.CAPTURE_ID: self.capture_id,
            self.ORDER_ID: self.order_id,
        }

    @classmethod
    def form_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        capture_id = dictionary.get(cls.CAPTURE_ID, None)
        order_id = dictionary.get(cls.ORDER_ID, None)

        # Return an object of this model
        return cls(
            capture_id=capture_id,
            order_id=order_id,

        )
