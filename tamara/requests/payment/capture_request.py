from tamara.models.money import Money
from tamara.models.order.item import Item
from tamara.models.shipping_info import ShippingInfo


class CaptureRequest(object):
    """
    Merchants can partially or fully capture an order after the order is shipped to the customer
    depending on partial shipment or full shipment.
    """

    ORDER_ID = 'order_id'
    TOTAL_AMOUNT = 'total_amount'
    TAX_AMOUNT = 'tax_amount'
    SHIPPING_AMOUNT = 'shipping_amount'
    DISCOUNT_AMOUNT = 'discount_amount'
    ITEMS = 'items'
    SHIPPING_INFO = 'shipping_info'

    def __init__(
            self,
            order_id: str,
            total_amount: Money,
            tax_amount: Money = None,
            shipping_amount: Money = None,
            discount_amount: Money = None,
            items: list = None,
            shipping_info: ShippingInfo = None,
    ):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.order_id = order_id
        self.total_amount = total_amount
        self.tax_amount = tax_amount
        self.shipping_amount = shipping_amount
        self.discount_amount = discount_amount
        self.items = items if items else []
        self.shipping_info = shipping_info

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.ORDER_ID: self.order_id,
            self.TOTAL_AMOUNT: self.total_amount.to_dictionary(),
            self.SHIPPING_AMOUNT: self.shipping_amount.to_dictionary() if self.shipping_amount else None,
            self.TAX_AMOUNT: self.tax_amount.to_dictionary() if self.tax_amount else None,
            self.DISCOUNT_AMOUNT: self.discount_amount.to_dictionary() if self.discount_amount else None,
            self.ITEMS: [item.to_dictionary() for item in self.items],
            self.SHIPPING_INFO: self.shipping_info.to_dictionary() if self.shipping_info else None,
        }

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        order_id = dictionary.get(cls.ORDER_ID, None)
        total_amount = Money.from_dictionary(dictionary.get(cls.TOTAL_AMOUNT))
        shipping_amount = Money.from_dictionary(dictionary.get(cls.SHIPPING_AMOUNT, None))
        tax_amount = Money.from_dictionary(dictionary.get(cls.TAX_AMOUNT, None))
        discount_amount = Money.from_dictionary(dictionary.get(cls.DISCOUNT_AMOUNT, None))
        items = dictionary.get(cls.ITEMS, None)
        items = [Item.from_dictionary(item) for item in items] if items else None
        shipping_info = ShippingInfo.from_dictionary(dictionary.get(cls.SHIPPING_INFO, None))

        # Return an object of this model
        return cls(
            order_id=order_id,
            total_amount=total_amount,
            shipping_amount=shipping_amount,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            items=items,
            shipping_info=shipping_info,
        )
