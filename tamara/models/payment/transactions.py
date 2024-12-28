from tamara.models.payment.cancel import Cancel
from tamara.models.payment.capture import Capture
from tamara.models.payment.refund import Refund


class Transactions(object):
    """
    This class is used to represent transactions as it consists of cancels, captures and refunds.
    """

    CANCELS = 'cancels'
    CAPTURES = 'captures'
    REFUNDS = 'refunds'

    def __init__(self, cancels: list = None, captures: list = None, refunds: str = None):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.cancels = cancels if cancels else []
        self.captures = captures if captures else []
        self.refunds = refunds if refunds else []

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.CANCELS: [cancel.to_dictionary() for cancel in self.cancels],
            self.CAPTURES: [capture.to_dictionary() for capture in self.captures],
            self.REFUNDS: [refund.to_dictionary() for refund in self.refunds],
        }

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        cancels = dictionary.get(cls.CANCELS, None)
        captures = dictionary.get(cls.CAPTURES, None)
        refunds = dictionary.get(cls.REFUNDS, None)

        if cancels is not None:
            cancels = [Cancel.from_dictionary(cancel) for cancel in cancels]

        if captures is not None:
            captures = [Capture.from_dictionary(capture) for capture in captures]

        if refunds is not None:
            refunds = [Refund.from_dictionary(refund) for refund in refunds]

        # Return an object of this model
        return cls(
            cancels=cancels,
            captures=captures,
            refunds=refunds,
        )
