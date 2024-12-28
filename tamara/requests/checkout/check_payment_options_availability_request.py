from tamara.models.money import Money


class CheckPaymentOptionsAvailabilityRequest(object):
    """
    Check if there are any available payment options for customer with the given order value
    """

    COUNTRY = 'country'
    ORDER_VALUE = 'order_value'
    PHONE_NUMBER = 'phone_number'
    IS_VIP = 'is_vip'

    def __init__(self, country: str, order_value: Money, phone_number: str, is_vip: bool = False):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.country = country
        self.order_value = order_value
        self.phone_number = phone_number
        self.is_vip = is_vip

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.COUNTRY: self.country,
            self.ORDER_VALUE: self.order_value.to_dictionary(),
            self.PHONE_NUMBER: self.phone_number,
            self.IS_VIP: self.is_vip,
        }

    @classmethod
    def form_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        country = dictionary.get(cls.COUNTRY)
        order_value = Money.from_dictionary(dictionary.get(cls.ORDER_VALUE))
        phone_number = dictionary.get(cls.PHONE_NUMBER)
        is_vip = dictionary.get(cls.IS_VIP)

        # Return an object of this model
        return cls(country=country, order_value=order_value, phone_number=phone_number, is_vip=is_vip)
