from tamara.models.money import Money
from tamara.models.shipping_info import ShippingInfo
from tamara.models.order.item import Item


class Capture(object):
    """
    This class is used to represent cancel as it consists of cancel_id, total_amount, name and items.
    """

    CAPTURE_ID = 'capture_id'
    ORDER_ID = 'order_id'
    TOTAL_AMOUNT = 'total_amount'
    REFUNDED_AMOUNT = 'refunded_amount'
    SHIPPING_AMOUNT = 'shipping_amount'
    TAX_AMOUNT = 'tax_amount'
    DISCOUNT_AMOUNT = 'discount_amount'
    SHIPPING_INFO = 'shipping_info'
    ITEMS = 'items'
    CREATED_AT = 'created_at'

    def __init__(
            self,
            capture_id: str = None,
            order_id: str = None,
            total_amount: Money = None,
            refunded_amount: Money = None,
            shipping_amount: Money = None,
            tax_amount: Money = None,
            discount_amount: Money = None,
            shipping_info: ShippingInfo = None,
            items: list = None, created_at: str = None
    ):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.capture_id = capture_id
        self.order_id = order_id
        self.total_amount = total_amount
        self.refunded_amount = refunded_amount
        self.shipping_amount = shipping_amount
        self.tax_amount = tax_amount
        self.discount_amount = discount_amount
        self.shipping_info = shipping_info
        self.items = items if items else []
        self.created_at = created_at

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.CAPTURE_ID: self.capture_id,
            self.ORDER_ID: self.order_id,
            self.TOTAL_AMOUNT: self.total_amount.to_dictionary() if self.total_amount else None,
            self.REFUNDED_AMOUNT: self.refunded_amount.to_dictionary() if self.refunded_amount else None,
            self.SHIPPING_AMOUNT: self.shipping_amount.to_dictionary() if self.shipping_amount else None,
            self.TAX_AMOUNT: self.tax_amount.to_dictionary() if self.tax_amount else None,
            self.DISCOUNT_AMOUNT: self.discount_amount.to_dictionary() if self.discount_amount else None,
            self.SHIPPING_INFO: self.shipping_info.to_dictionary() if self.shipping_info else None,
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
        capture_id = dictionary.get(cls.CAPTURE_ID, None)
        order_id = dictionary.get(cls.ORDER_ID, None)
        total_amount = Money.from_dictionary(dictionary.get(cls.TOTAL_AMOUNT, None))
        refunded_amount = Money.from_dictionary(dictionary.get(cls.REFUNDED_AMOUNT, None))
        shipping_amount = Money.from_dictionary(dictionary.get(cls.SHIPPING_AMOUNT, None))
        tax_amount = Money.from_dictionary(dictionary.get(cls.TAX_AMOUNT, None))
        discount_amount = Money.from_dictionary(dictionary.get(cls.DISCOUNT_AMOUNT, None))
        shipping_info = ShippingInfo.from_dictionary(dictionary.get(cls.SHIPPING_INFO, None))
        items = dictionary.get(cls.ITEMS, None)
        items = [Item.from_dictionary(item) for item in items] if items else None
        created_at = dictionary.get(cls.CREATED_AT)

        # Return an object of this model
        return cls(
            capture_id=capture_id,
            order_id=order_id,
            total_amount=total_amount,
            refunded_amount=refunded_amount,
            shipping_amount=shipping_amount,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            shipping_info=shipping_info,
            items=items,
            created_at=created_at,
        )
