from tamara.models.money import Money
from tamara.models.order.address import Address
from tamara.models.order.consumer import Consumer
from tamara.models.order.discount import Discount
from tamara.models.order.merchant import Merchant
from tamara.models.order.item import Item


class Order(object):
    """
    This class is used to represent order as it consists of order_id, total_amount, items and others.
    """

    ORDER_REFERENCE_ID = 'order_reference_id'
    TOTAL_AMOUNT = 'total_amount'
    DESCRIPTION = 'description'
    COUNTRY_CODE = 'country_code'
    PAYMENT_TYPE = 'payment_type'
    ITEMS = 'items'
    CONSUMER = 'consumer'
    SHIPPING_ADDRESS = 'shipping_address'
    TAX_AMOUNT = 'tax_amount'
    SHIPPING_AMOUNT = 'shipping_amount'
    MERCHANT_URL = 'merchant_url'
    ORDER_NUMBER = 'order_number'
    INSTALMENTS = 'instalments'
    LOCALE = 'locale'
    BILLING_ADDRESS = 'billing_address'
    DISCOUNT = 'discount'
    PLATFORM = 'platform'
    IS_MOBILE = 'is_mobile'
    EXPIRES_IN_MINUTES = 'expires_in_minutes'

    def __init__(
            self,
            order_reference_id: str,
            total_amount: Money,
            description: str,
            country_code: str,
            payment_type: str,
            items: list,
            consumer: Consumer,
            shipping_address: Address,
            tax_amount: Money,
            shipping_amount: Money,
            merchant_url: Merchant,
            order_number: str = None,
            instalments: int = None,
            discount: Discount = None,
            locale: str = None,
            billing_address: Address = None,
            platform: str = None,
            is_mobile: bool = None,
            expires_in_minutes: bool = None,
    ):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """

        self.order_reference_id = order_reference_id
        self.total_amount = total_amount
        self.description = description
        self.country_code = country_code
        self.payment_type = payment_type
        self.items = items
        self.consumer = consumer
        self.shipping_address = shipping_address
        self.tax_amount = tax_amount
        self.shipping_amount = shipping_amount
        self.merchant_url = merchant_url
        self.order_number = order_number
        self.instalments = instalments
        self.discount = discount
        self.locale = locale
        self.billing_address = billing_address
        self.platform = platform
        self.is_mobile = is_mobile
        self.expires_in_minutes = expires_in_minutes

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.ORDER_REFERENCE_ID: self.order_reference_id,
            self.ORDER_NUMBER: self.order_number,
            self.INSTALMENTS: self.instalments,
            self.PAYMENT_TYPE: self.payment_type,
            self.CONSUMER: self.consumer.to_dictionary(),
            self.COUNTRY_CODE: self.country_code,
            self.DESCRIPTION: self.description,
            self.LOCALE: self.locale,
            self.PLATFORM: self.platform,
            self.IS_MOBILE: self.is_mobile,
            self.EXPIRES_IN_MINUTES: self.expires_in_minutes,
            self.ITEMS: [item.to_dictionary() for item in self.items],
            self.TOTAL_AMOUNT: self.total_amount.to_dictionary(),
            self.SHIPPING_AMOUNT: self.shipping_amount.to_dictionary(),
            self.DISCOUNT: self.discount.to_dictionary() if self.discount else None,
            self.TAX_AMOUNT: self.tax_amount.to_dictionary(),
            self.SHIPPING_ADDRESS: self.shipping_address.to_dictionary(),
            self.BILLING_ADDRESS: self.billing_address.to_dictionary() if self.billing_address else None,
            self.MERCHANT_URL: self.merchant_url.to_dictionary(),
        }

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        order_reference_id = dictionary.get(cls.ORDER_REFERENCE_ID)
        order_number = dictionary.get(cls.ORDER_NUMBER, None)
        instalments = dictionary.get(cls.INSTALMENTS, None)
        payment_type = dictionary.get(cls.PAYMENT_TYPE)
        consumer = Consumer.form_dictionary(dictionary.get(cls.CONSUMER))
        country_code = dictionary.get(cls.COUNTRY_CODE)
        description = dictionary.get(cls.DESCRIPTION)
        locale = dictionary.get(cls.LOCALE, None)
        platform = dictionary.get(cls.PLATFORM, None)
        is_mobile = dictionary.get(cls.IS_MOBILE, None)
        expires_in_minutes = dictionary.get(cls.EXPIRES_IN_MINUTES, None)

        items = [Item.from_dictionary(item) for item in dictionary.get(cls.ITEMS)]

        total_amount = Money.from_dictionary(dictionary.get(cls.TOTAL_AMOUNT))
        shipping_amount = Money.from_dictionary(dictionary.get(cls.SHIPPING_AMOUNT))
        discount = Discount.from_dictionary(dictionary.get(cls.DISCOUNT, None))
        tax_amount = Money.from_dictionary(dictionary.get(cls.TAX_AMOUNT))

        shipping_address = Address.from_dictionary(dictionary.get(cls.SHIPPING_ADDRESS))
        billing_address = Address.from_dictionary(dictionary.get(cls.BILLING_ADDRESS, None))

        merchant_url = Merchant.from_dictionary(dictionary.get(cls.MERCHANT_URL))

        # Return an object of this model
        return cls(
            order_reference_id=order_reference_id,
            order_number=order_number,
            instalments=instalments,
            payment_type=payment_type,
            consumer=consumer,
            country_code=country_code,
            description=description,
            locale=locale,
            platform=platform,
            is_mobile=is_mobile,
            expires_in_minutes=expires_in_minutes,
            items=items,
            total_amount=total_amount,
            shipping_amount=shipping_amount,
            discount=discount,
            tax_amount=tax_amount,
            shipping_address=shipping_address,
            billing_address=billing_address,
            merchant_url=merchant_url,
        )
