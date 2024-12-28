from tamara.handlers.handler import Handler
from tamara.helpers.api_helper import APIHelper
from tamara.requests.payment.capture_request import CaptureRequest
from tamara.responses.payment.capture_response import CaptureResponse


class CaptureHandler(Handler):
    """
    Merchants can partially or fully capture an order after the order is shipped to the customer
    depending on partial shipment or full shipment.
    """

    path = '/payments/capture'
    response_model = CaptureResponse

    def __call__(self, request: CaptureRequest):
        """
        In Python, classes, methods, and instances are callable because calling a class returns a new instance.
        Instances are callable if their class includes __call__() method.
        """
        parameters = request.to_dictionary()
        request = self.http_client.post(self.path, parameters=parameters)
        context = self.execute_request(request)
        return APIHelper.json_deserialize(context.response.raw_body, self.response_model.form_dictionary)


capture = CaptureHandler()
