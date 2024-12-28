from tamara.handlers.handler import Handler
from tamara.helpers.api_helper import APIHelper
from tamara.requests.checkout.create_checkout_session_request import CreateCheckoutSessionRequest
from tamara.responses.checkout.create_checkout_session_response import CreateCheckoutSessionResponse


class CreateCheckoutSessionHandler(Handler):
    """
    Create a checkout session and pass through all the payment information in the request.
    The response will have order_id, checkout_id and checkout_url.
    Please retain the order_id to fetch the information about the order later
    and redirect the customer to checkout_url to complete the transaction via Tamara.
    """

    path = '/checkout'
    response_model = CreateCheckoutSessionResponse

    def __call__(self, request: CreateCheckoutSessionRequest):
        """
        In Python, classes, methods, and instances are callable because calling a class returns a new instance.
        Instances are callable if their class includes __call__() method.
        """
        parameters = request.to_dictionary()
        request = self.http_client.post(self.path, parameters=parameters)
        context = self.execute_request(request)
        return APIHelper.json_deserialize(context.response.raw_body, self.response_model.form_dictionary)


create_checkout_session = CreateCheckoutSessionHandler()
