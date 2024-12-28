from tamara.models.money import Money


class Item(object):
    """
    This class is used to represent item as it consists of reference_id, type, name and others.
    """

    REFERENCE_ID = 'reference_id'
    TYPE = 'type'
    NAME = 'name'
    SKU = 'sku'
    QUANTITY = 'quantity'
    TOTAL_AMOUNT = 'total_amount'
    IMAGE_URL = 'image_url'
    UNIT_PRICE = 'unit_price'
    DISCOUNT_AMOUNT = 'discount_amount'
    TAX_AMOUNT = 'tax_amount'

    def __init__(
            self,
            reference_id: str,
            type: str,
            name: str,
            sku: str,
            quantity: int,
            total_amount: Money,
            image_url: str = None,
            unit_price: Money = None,
            discount_amount: Money = None,
            tax_amount: Money = None,
    ):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.reference_id = reference_id
        self.type = type
        self.name = name
        self.sku = sku
        self.quantity = quantity
        self.total_amount = total_amount
        self.image_url = image_url
        self.unit_price = unit_price
        self.discount_amount = discount_amount
        self.tax_amount = tax_amount

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.REFERENCE_ID: self.reference_id,
            self.TYPE: self.type,
            self.NAME: self.name,
            self.SKU: self.sku,
            self.IMAGE_URL: self.image_url,
            self.QUANTITY: self.quantity,
            self.TOTAL_AMOUNT: self.total_amount.to_dictionary(),
            self.UNIT_PRICE: self.unit_price.to_dictionary() if self.unit_price else None,
            self.DISCOUNT_AMOUNT: self.discount_amount.to_dictionary() if self.discount_amount else None,
            self.TAX_AMOUNT: self.tax_amount.to_dictionary() if self.tax_amount else None,

        }

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        reference_id = dictionary.get(cls.REFERENCE_ID)
        type = dictionary.get(cls.TYPE)

        name = dictionary.get(cls.NAME)
        sku = dictionary.get(cls.SKU)
        image_url = dictionary.get(cls.IMAGE_URL, None)

        quantity = dictionary.get(cls.QUANTITY)
        total_amount = Money.from_dictionary(dictionary.get(cls.TOTAL_AMOUNT))
        unit_price = Money.from_dictionary(dictionary.get(cls.UNIT_PRICE, None))
        discount_amount = Money.from_dictionary(dictionary.get(cls.DISCOUNT_AMOUNT, None))
        tax_amount = Money.from_dictionary(dictionary.get(cls.TAX_AMOUNT, None))

        # Return an object of this model
        return cls(
            reference_id=reference_id,
            type=type,
            name=name,
            sku=sku,
            image_url=image_url,
            quantity=quantity,
            total_amount=total_amount,
            unit_price=unit_price,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
        )
