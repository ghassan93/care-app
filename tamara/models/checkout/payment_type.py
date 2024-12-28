from tamara.models.checkout.instalment import Instalment
from tamara.models.money import Money


class PaymentType(object):
    """
    This class is used to represent payment type as it consists of name, description,
    min_limit, max_limit and supported_instalments .
    """
    NAME = 'name'
    DESCRIPTION = 'description'
    MIN_LIMIT = 'min_limit'
    MAX_LIMIT = 'max_limit'
    SUPPORTED_INSTALMENTS = 'supported_instalments'

    def __init__(self, name: str, description: str, min_limit: Money, max_limit: Money, supported_instalments: list):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.name = name
        self.description = description
        self.min_limit = min_limit
        self.max_limit = max_limit
        self.supported_instalments = supported_instalments

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.NAME: self.name,
            self.DESCRIPTION: self.description,
            self.MIN_LIMIT: self.min_limit.to_dictionary(),
            self.MAX_LIMIT: self.max_limit.to_dictionary(),
            self.SUPPORTED_INSTALMENTS: [instalment.to_dictionary() for instalment in self.supported_instalments]
        }

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        name = dictionary.get(cls.NAME)
        description = dictionary.get(cls.DESCRIPTION)

        min_limit = Money.from_dictionary(dictionary.get(cls.MIN_LIMIT))
        max_limit = Money.from_dictionary(dictionary.get(cls.MAX_LIMIT))

        supported_instalments = [
            Instalment.from_dictionary(instalment) for instalment in
            dictionary.get(cls.SUPPORTED_INSTALMENTS)
        ]

        # Return an object of this model
        return cls(
            name=name,
            description=description,
            min_limit=min_limit,
            max_limit=max_limit,
            supported_instalments=supported_instalments
        )
