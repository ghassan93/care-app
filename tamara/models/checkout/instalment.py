from tamara.models.money import Money


class Instalment(object):
    """
    This class is used to represent instalment as it consists of instalments, min_limit and max_limit.
    """

    INSTALMENTS = 'instalments'
    MIN_LIMIT = 'min_limit'
    MAX_LIMIT = 'max_limit'

    def __init__(self, instalments: str, min_limit: Money, max_limit: Money):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.instalments = instalments
        self.min_limit = min_limit
        self.max_limit = max_limit

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.INSTALMENTS: self.instalments,
            self.MIN_LIMIT: self.min_limit.to_dictionary(),
            self.MAX_LIMIT: self.max_limit.to_dictionary()
        }

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        instalments = dictionary.get(cls.INSTALMENTS)

        min_limit = Money.from_dictionary(dictionary=dictionary.get(cls.MIN_LIMIT))
        max_limit = Money.from_dictionary(dictionary=dictionary.get(cls.MAX_LIMIT))

        # Return an object of this model
        return cls(instalments=instalments, min_limit=min_limit, max_limit=max_limit)
