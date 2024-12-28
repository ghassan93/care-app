class AuthoriseOrderResponse(object):
    """
    Merchant will be required to call to Authorize API the order after receiving the notification from Tamara
    about the order being ‘Approved’.
    This is one of the most important flows the merchant needs to complete.
    """

    ORDER_ID = 'order_id'
    STATUS = 'status'
    ORDER_EXPIRY_TIME = 'order_expiry_time'
    PAYMENT_TYPE = 'payment_type'
    AUTO_CAPTURED = 'auto_captured'

    def __init__(
            self,
            order_id: str = None,
            status: str = None,
            order_expiry_time: str = None,
            payment_type: str = None,
            auto_captured: bool = None
    ):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """

        self.order_id = order_id
        self.status = status
        self.order_expiry_time = order_expiry_time
        self.payment_type = payment_type
        self.auto_captured = auto_captured

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.ORDER_ID: self.order_id,
            self.STATUS: self.status,
            self.ORDER_EXPIRY_TIME: self.order_expiry_time,
            self.PAYMENT_TYPE: self.payment_type,
            self.AUTO_CAPTURED: self.auto_captured,
        }

    @classmethod
    def form_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        order_id = dictionary.get(cls.ORDER_ID, None)
        status = dictionary.get(cls.STATUS, None)
        order_expiry_time = dictionary.get(cls.ORDER_EXPIRY_TIME, None)
        payment_type = dictionary.get(cls.PAYMENT_TYPE, None)
        auto_captured = dictionary.get(cls.AUTO_CAPTURED, None)

        # Return an object of this model
        return cls(
            order_id=order_id,
            status=status,
            order_expiry_time=order_expiry_time,
            payment_type=payment_type,
            auto_captured=auto_captured
        )
