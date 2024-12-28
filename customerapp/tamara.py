import uuid

from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone

from tamara.client import TamaraClient
from tamara.models.money import Money
from tamara.models.order.address import Address
from tamara.models.order.consumer import Consumer
from tamara.models.order.discount import Discount
from tamara.models.order.item import Item
from tamara.models.order.merchant import Merchant
from tamara.models.order.order import Order
from tamara.models.shipping_info import ShippingInfo
from tamara.requests.checkout.create_checkout_session_request import CreateCheckoutSessionRequest
from tamara.requests.order.authorise_order_request import AuthoriseOrderRequest
from tamara.requests.payment.capture_request import CaptureRequest


class Tamara(object):
    """
    This class used to handle alrajhi provider payment
    it has some function for get operations success and secure
    """

    def __init__(self, request, is_sandbox_env=False):
        """
        Welcome to our API reference! We're happy that you've decided to explore our REST APIs.
        To get started, you'll first need access to a sandbox/production account,
        set up your sandbox/production environment,
        and get access to API and Notification token for the sandbox/production environments.
        """
        api_token = settings.TAMARA_API_TOKEN
        self.client = TamaraClient(api_token, is_sandbox_env=is_sandbox_env)
        self.request = request

    def get_absolute_uri(self, url_name):
        """
        This function is used to return the absolute uri.
        """

        url = reverse_lazy(url_name)
        return self.request.build_absolute_uri(url)

    def get_order_reference_id(self):
        """
        The unique order id from merchant side,
        this will be used with the settlement and reports
        """
        return uuid.uuid1().int.__str__()

    def get_order_number(self, order):
        """
        The order number from the merchant side, this will be used for communication with the customer.
        If not passed, it will take the order_reference_id value
        """
        return order.pk

    def get_payment_type(self):
        """
        Value: "PAY_BY_INSTALMENTS"
        """
        return 'PAY_BY_INSTALMENTS'

    def get_country_code(self):
        """
        This Function is used to return country code
        @return: country code
        """
        return 'SA'

    def get_currency_code(self):
        """
        The two-character ISO 3166-1 country code e.g SA or AE
        """
        return 'SAR'

    def get_description_value(self, order):
        """
        The order description. Limited to 256 characters.
        """
        return 'دفع قيمة الطلب {} من خلال بوابة الدفع تمارا'.format(order.pk)

    def get_total_amount(self, price):
        """
        Total amount to be charged to consumer, not including any discount amount
        """
        return Money(amount=price, currency=self.get_currency_code())

    def get_discount_amount(self, discount):
        """
        This function is used to return the discount amount from price.
        """
        amount = Money(amount=discount, currency=self.get_currency_code())
        return Discount(name="", amount=amount)

    def get_tax_amount(self, tax):
        """
        This function is used to return the tax amount from price.
        """
        return Money(amount=tax, currency=self.get_currency_code())

    def get_shipping_amount(self):
        """
        This function is return tax amount
        """
        return Money(amount=0.0, currency=self.get_currency_code())

    def get_order_items(self, order):
        """
        Array of objects representing the order items in this order
        """
        items = []
        for order_item in order.order_item.all():
            item = Item(
                reference_id=order_item.pk,
                type="Digital",
                name=order_item.sales.content_object.name,
                sku='SA-{}'.format(order_item.pk),
                quantity=1,
                unit_price=Money(amount=order_item.get_price_value, currency=self.get_currency_code()),
                discount_amount=Money(amount=order_item.get_discount_value, currency=self.get_currency_code()),
                tax_amount=Money(amount=order_item.get_tax_value, currency=self.get_currency_code()),
                total_amount=Money(amount=order_item.get_total_value, currency=self.get_currency_code()),
            )

            items.append(item)
        return items

    def get_consumer_object(self, order):
        """
        This function return the customer as it consists of first_name, last_name,
        phone_number and others.
        """

        user = order.customer.user
        return Consumer(
            first_name=user.first_name, last_name=user.last_name, phone_number=str(user.phonenumber),
            email=user.email,
        )

    def get_shipping_address(self, order):
        """
        This function return the address as it consists of first_name, last_name,
        line1 and others.
        """

        user = order.customer.user
        return Address(
            first_name=user.first_name,
            last_name=user.last_name,
            line1=user.profile.location or 'Jeddah',
            city=getattr(user.profile.city, 'name', 'Jeddah'),
            country_code=self.get_country_code()
        )

    def get_shipping_info(self):
        """
        This function return the shipping info as it consists of shipped_at and shipping_company.
        """

        return ShippingInfo(shipped_at=str(timezone.now()), shipping_company='Care company')

    def get_merchant_url(self):
        """
        This function return the merchant as it consists of success, failure, cancel
        and notification.
        """
        return Merchant(
            success=self.get_absolute_uri('customer:api:tamara-success'),
            failure=self.get_absolute_uri('customer:api:tamara-error'),
            cancel=self.get_absolute_uri('customer:api:tamara-cancel'),
            notification=self.get_absolute_uri('customer:api:tamara-notification'),
        )

    def create_checkout_session(self, order, total, discount, tax):
        """
        Create a checkout session and pass through all the payment information in the request.
        The response will have order_id, checkout_id and checkout_url.
        Please retain the order_id to fetch the information about the order later
        and redirect the customer to checkout_url to complete the transaction via Tamara.
        """

        order = Order(
            order_reference_id=self.get_order_reference_id(),
            order_number=self.get_order_number(order),
            total_amount=self.get_total_amount(total),
            description=self.get_description_value(order),
            country_code=self.get_country_code(),
            payment_type=self.get_payment_type(),
            items=self.get_order_items(order),
            consumer=self.get_consumer_object(order),
            shipping_address=self.get_shipping_address(order),
            tax_amount=self.get_tax_amount(tax),
            discount=self.get_discount_amount(discount),
            shipping_amount=self.get_shipping_amount(),
            merchant_url=self.get_merchant_url(),
        )

        request = CreateCheckoutSessionRequest(order)
        return self.client.create_checkout_session(request).to_dictionary()

    def authorise(self, order_id):
        """
        Merchant will be required to call to Authorize API the order after receiving the notification from
        Tamara about the order being ‘Approved’.
        """
        request = AuthoriseOrderRequest(order_id=order_id)
        return self.client.authorise_order(request).to_dictionary()

    def capture(self, order_id, total):
        """
        Merchants can partially or fully capture an order after the order is shipped to the customer depending
        on partial shipment or full shipment.
        """

        request = CaptureRequest(
            order_id=order_id,
            total_amount=self.get_total_amount(total),
            shipping_info=self.get_shipping_info()
        )

        return self.client.capture(request).to_dictionary()
