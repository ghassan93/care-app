from tamara.configuration import Configuration
from tamara.handlers.checkout import (
    get_payment_types_handler,
    check_payment_options_availability_handler,
    create_checkout_session_handler
)
from tamara.handlers.order import authorise_order_handler
from tamara.handlers.payment import capture_handler


class TamaraClient(object):
    config = Configuration

    def __init__(self, api_token, is_sandbox_env=False):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """

        Configuration.api_token = api_token

        if is_sandbox_env:
            Configuration.environment = Configuration.Environment.SANDBOX

    def get_payment_types(self, request):
        """
        List supporting payment types from Tamara for instance:
        Shop now, pay later or Instalment.
        """
        return get_payment_types_handler.get_payment_types(request=request)

    def check_payment_options_availability(self, request):
        """
        Check if there are any available payment options for customer
        with the given order value
        """
        return check_payment_options_availability_handler.check_payment_options_availability(request=request)

    def create_checkout_session(self, request):
        """
        Create a checkout session and pass through all the payment information in the request.
        The response will have order_id, checkout_id and checkout_url.
        Please retain the order_id to fetch the information about the order later
        and redirect the customer to checkout_url to complete the transaction via Tamara.
        """
        return create_checkout_session_handler.create_checkout_session(request=request)

    def authorise_order(self, request):
        """
        Merchant will be required to call to Authorize API the order after receiving the notification from Tamara
        about the order being ‘Approved’.
        This is one of the most important flows the merchant needs to complete.
        """
        return authorise_order_handler.authorise_order(request=request)

    def capture(self, request):
        """
        Merchants can partially or fully capture an order after the order is shipped to the customer depending on
        partial shipment or full shipment.
        """
        return capture_handler.capture(request=request)
