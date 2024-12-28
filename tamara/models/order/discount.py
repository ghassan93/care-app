from tamara.models.money import Money


class Discount(object):
    """
    This class is used to represent discount as it consists of name and amount.
    """
    NAME = 'name'
    AMOUNT = 'amount'

    def __init__(self, name: str, amount: Money):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.name = name
        self.amount = amount

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {self.NAME: self.name, self.AMOUNT: self.amount.to_dictionary()}

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        name = dictionary.get(cls.NAME)
        amount = Money.from_dictionary(dictionary.get(cls.AMOUNT))

        # Return an object of this model
        return cls(name=name, amount=amount)
