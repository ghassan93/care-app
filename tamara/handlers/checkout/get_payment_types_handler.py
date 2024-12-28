from tamara.handlers.handler import Handler
from tamara.helpers.api_helper import APIHelper
from tamara.requests.checkout.get_payment_request import GetPaymentTypesRequest
from tamara.responses.checkout.get_payment_types_response import GetPaymentTypesResponse


class GetPaymentTypesHandler(Handler):
    """
    List supporting payment types from Tamara for instance:
    Shop now, pay later or Instalment.
    """

    path = '/checkout/payment-types'
    response_model = GetPaymentTypesResponse

    def __call__(self, request: GetPaymentTypesRequest):
        """
        In Python, classes, methods, and instances are callable because calling a class returns a new instance.
        Instances are callable if their class includes __call__() method.
        """
        parameters = request.to_dictionary()
        url = APIHelper.append_url_with_query_parameters(self.path, parameters=parameters)
        request = self.http_client.get(url)
        context = self.execute_request(request)
        return APIHelper.json_deserialize(context.response.raw_body, self.response_model.form_dictionary)


get_payment_types = GetPaymentTypesHandler()
