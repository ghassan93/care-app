class GetPaymentTypesRequest(object):
    """
    List supporting payment types from Tamara for instance:
    Shop now, pay later or Instalment.
    """

    COUNTRY = 'country'
    CURRENCY = 'currency'
    ORDER_VALUE = 'order_value'
    PHONE = 'phone'

    def __init__(self, country: str, currency: str = None, order_value: str = None, phone: str = None):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.country = country
        self.currency = currency
        self.order_value = order_value
        self.phone = phone

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.COUNTRY: self.country,
            self.CURRENCY: self.currency,
            self.ORDER_VALUE: self.order_value,
            self.PHONE: self.phone,
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
        currency = dictionary.get(cls.CURRENCY)
        order_value = dictionary.get(cls.ORDER_VALUE)
        phone = dictionary.get(cls.PHONE)

        # Return an object of this model
        return cls(country=country, currency=currency, order_value=order_value, phone=phone)
