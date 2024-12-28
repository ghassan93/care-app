from tamara.handlers.handler import Handler
from tamara.helpers.api_helper import APIHelper
from tamara.requests.checkout.check_payment_options_availability_request import CheckPaymentOptionsAvailabilityRequest
from tamara.responses.checkout.check_payment_options_availability_response import \
    CheckPaymentOptionsAvailabilityResponse


class CheckPaymentOptionsAvailabilityHandler(Handler):
    """
    List supporting payment types from Tamara for instance:
    Shop now, pay later or Instalment.
    """

    path = '/checkout/payment-options-pre-check'
    response_model = CheckPaymentOptionsAvailabilityResponse

    def __call__(self, request: CheckPaymentOptionsAvailabilityRequest):
        """
        In Python, classes, methods, and instances are callable because calling a class returns a new instance.
        Instances are callable if their class includes __call__() method.
        """
        parameters = request.to_dictionary()
        request = self.http_client.post(self.path, parameters=parameters)
        context = self.execute_request(request)
        return APIHelper.json_deserialize(context.response.raw_body, self.response_model.form_dictionary)


check_payment_options_availability = CheckPaymentOptionsAvailabilityHandler()
