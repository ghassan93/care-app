from tamara.models.money import Money
from tamara.models.order.item import Item


class Refund(object):
    """
    This class is used to represent refunds as it consists of refund_id, capture_id, total_amount and others.
    """

    REFUND_ID = 'refund_id'
    CAPTURE_ID = 'capture_id'
    TOTAL_AMOUNT = 'total_amount'
    ITEMS = 'items'
    CREATED_AT = 'created_at'
    COMMENT = 'comment'

    def __init__(
            self,
            refund_id: str = None,
            capture_id: str = None,
            total_amount: Money = None,
            items: list = None,
            created_at: str = None,
            comment: str = None
    ):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.refund_id = refund_id
        self.capture_id = capture_id
        self.total_amount = total_amount
        self.items = items if items else []
        self.created_at = created_at
        self.comment = comment

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.REFUND_ID: self.refund_id,
            self.CAPTURE_ID: self.capture_id,
            self.TOTAL_AMOUNT: self.total_amount.to_dictionary() if self.total_amount else None,
            self.ITEMS: [item.to_dictionary() for item in self.items],
            self.CREATED_AT: self.created_at,
            self.COMMENT: self.comment,
        }

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        refund_id = dictionary.get(cls.REFUND_ID, None)
        capture_id = dictionary.get(cls.CAPTURE_ID, None)
        total_amount = Money.from_dictionary(dictionary.get(cls.TOTAL_AMOUNT, None))
        items = dictionary.get(cls.ITEMS, None)
        items = [Item.from_dictionary(item) for item in items] if items else None
        created_at = dictionary.get(cls.CREATED_AT, None)
        comment = dictionary.get(cls.COMMENT, None)

        # Return an object of this model
        return cls(
            refund_id=refund_id,
            capture_id=capture_id,
            total_amount=total_amount,
            items=items,
            created_at=created_at,
            comment=comment
        )
