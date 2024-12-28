from tamara.models.checkout.payment_type import PaymentType


class GetPaymentTypesResponse(object):
    """
    List supporting payment types from Tamara for instance:
    Shop now, pay later or Instalment.
    """

    PAYMENT_TYPES = 'payment_types'

    def __init__(self, payment_types: list):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """

        self.payment_types = payment_types

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {self.PAYMENT_TYPES: [payment_type.to_dictionary() for payment_type in self.payment_types]}

    @classmethod
    def form_dictionary(cls, data: list):
        """
        Creates an instance of this model from a dictionary
        """

        if data is None:
            return None

        # Extract variables from the dictionary
        payment_types = [PaymentType.from_dictionary(payment_type) for payment_type in data]

        # Return an object of this model
        return cls(payment_types=payment_types)
