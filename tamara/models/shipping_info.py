class ShippingInfo(object):
    """
    This class is used to represent shipping_info as it consists of shipped_at, shipping_company,
    tracking_number and others.
    """

    SHIPPED_AT = 'shipped_at'
    SHIPPING_COMPANY = 'shipping_company'
    TRACKING_NUMBER = 'tracking_number'
    TRACKING_URL = 'tracking_url'

    def __init__(
            self, shipped_at: str, shipping_company: str, tracking_number: str = None,
            tracking_url: str = None
    ):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.shipped_at = shipped_at
        self.shipping_company = shipping_company
        self.tracking_number = tracking_number
        self.tracking_url = tracking_url

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.SHIPPED_AT: self.shipped_at,
            self.SHIPPING_COMPANY: self.shipping_company,
            self.TRACKING_NUMBER: self.tracking_number,
            self.TRACKING_URL: self.tracking_url,

        }

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        shipped_at = dictionary.get(cls.SHIPPED_AT)
        shipping_company = dictionary.get(cls.SHIPPING_COMPANY)

        tracking_number = dictionary.get(cls.TRACKING_NUMBER, None)
        tracking_url = dictionary.get(cls.TRACKING_URL, None)

        # Return an object of this model
        return cls(
            shipped_at=shipped_at,
            shipping_company=shipping_company,
            tracking_number=tracking_number,
            tracking_url=tracking_url,
        )
