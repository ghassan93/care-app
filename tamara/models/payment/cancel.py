from tamara.models.money import Money
from tamara.models.order.item import Item


class Cancel(object):
    """
    This class is used to represent cancel as it consists of cancel_id, total_amount, name and items.
    """

    CANCEL_ID = 'cancel_id'
    ORDER_ID = 'order_id'
    TOTAL_AMOUNT = 'total_amount'
    ITEMS = 'items'
    CREATED_AT = 'created_at'

    def __init__(
            self,
            cancel_id: str = None,
            order_id: str = None,
            total_amount: Money = None,
            items: list = None,
            created_at: str = None
    ):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.cancel_id = cancel_id
        self.order_id = order_id
        self.total_amount = total_amount
        self.items = items if items else []
        self.created_at = created_at

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.CANCEL_ID: self.cancel_id,
            self.ORDER_ID: self.order_id,
            self.TOTAL_AMOUNT: self.total_amount.to_dictionary() if self.total_amount else None,
            self.ITEMS: [item.to_dictionary() for item in self.items],
            self.CREATED_AT: self.created_at

        }

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        cancel_id = dictionary.get(cls.CANCEL_ID, None)
        order_id = dictionary.get(cls.ORDER_ID, None)
        total_amount = Money.from_dictionary(dictionary.get(cls.TOTAL_AMOUNT, None))
        items = dictionary.get(cls.ITEMS, None)
        items = [Item.from_dictionary(item) for item in items] if items else None
        created_at = dictionary.get(cls.CREATED_AT, None)

        # Return an object of this model
        return cls(
            cancel_id=cancel_id,
            order_id=order_id,
            total_amount=total_amount,
            items=items,
            created_at=created_at
        )
