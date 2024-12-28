from tamara.handlers.handler import Handler
from tamara.helpers.api_helper import APIHelper
from tamara.requests.order.authorise_order_request import AuthoriseOrderRequest
from tamara.responses.order.authorise_order_response import AuthoriseOrderResponse


class AuthoriseOrderHandler(Handler):
    """
    Merchant will be required to call to Authorize API the order after receiving the notification from Tamara
    about the order being ‘Approved’.
    This is one of the most important flows the merchant needs to complete.
    """

    path = '/orders/{order_id}/authorise'
    response_model = AuthoriseOrderResponse

    def __call__(self, request: AuthoriseOrderRequest):
        """
        In Python, classes, methods, and instances are callable because calling a class returns a new instance.
        Instances are callable if their class includes __call__() method.
        """
        self.path = self.path.format(order_id=request.order_id)
        request = self.http_client.post(self.path)
        context = self.execute_request(request)
        return APIHelper.json_deserialize(context.response.raw_body, self.response_model.form_dictionary)


authorise_order = AuthoriseOrderHandler()
