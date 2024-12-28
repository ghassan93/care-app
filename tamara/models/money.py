class Money(object):
    """
    This class is used to represent money as it consists of amount and currency.
    """
    AMOUNT = 'amount'
    CURRENCY = 'currency'

    def __init__(self, amount: float, currency: str):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.amount = amount
        self.currency = currency

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {self.AMOUNT: self.amount, self.CURRENCY: self.currency}

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        amount = dictionary.get(cls.AMOUNT)
        currency = dictionary.get(cls.CURRENCY)

        # Return an object of this model
        return cls(amount=amount, currency=currency)
