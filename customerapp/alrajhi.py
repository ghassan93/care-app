import json
import uuid
from urllib import parse

import requests
from django.conf import settings
from django.urls import reverse_lazy

from .crypt import encrypt, decrypt


class Alrajhi(object):
    """
    This class used to handle alrajhi provider payment
    it has some function for get operations success and secure
    """

    URL = 'https://digitalpayments.alrajhibank.com.sa/pg/payment/hosted.htm'

    def __init__(self, request):
        """
        the constructor function for alrajhi payment provider
        """
        self.request = request
        self.endpoint = self.URL

    @property
    def resource(self):
        """
        this function used to get private key
        @return: private_key
        """
        return getattr(settings, f'CARE_PAYMENT_RESOURCE').encode("utf8")

    @property
    def vector(self):
        """
        this function used to get initialization vector value
        @return: private_key
        """
        return settings.CARE_PAYMENT_IV.encode("utf8")

    @property
    def password(self):
        """
        this function is used to get care password provider
        @return: password
        """
        return getattr(settings, f'CARE_PAYMENT_PASSWORD')

    @property
    def identifier(self):
        """
        this function is used to get care id provider
        @return: id
        """
        return getattr(settings, f'CARE_PAYMENT_ID')

    @property
    def currency_code(self):
        """
        this function is used to get currency code
        @return: password
        """
        return settings.CARE_PAYMENT_CURRENCYCODE

    @property
    def success_url(self):
        """
        this function is used to get success url
        @return: password
        """
        url = reverse_lazy('customer:api:alrajhi-success')
        return self.request.build_absolute_uri(url)

    @property
    def error_url(self):
        """
        this function is used to get error url
        @return: password
        """
        url = reverse_lazy('customer:api:alrajhi-error')
        return self.request.build_absolute_uri(url)

    def trandata(self, amt, track):
        """
        this function used to get trandata value
        @return: trandata
        """

        trandata = [
            {
                "action": "1",
                "amt": amt,
                "currencyCode": self.currency_code,
                "errorURL": self.error_url,
                "id": self.identifier,
                "password": self.password,
                "responseURL": self.success_url,
                "trackId": track
            }
        ]
        return encrypt(json.dumps(trandata), self.resource, self.vector)

    def body(self, trandata):
        """
        this function used to hand raw data for request tp alrajhi provider
        @return: body
        """

        return json.dumps([{
            "id": self.identifier, "trandata": trandata,
            "responseURL": self.success_url, "errorURL": self.error_url
        }])

    def post(self, data):
        """
        this function is used for request alrajhi payment provider
        @return: HTTP response
        """
        headers = {'content-type': 'application/json'}
        return requests.post(self.endpoint, data=data, headers=headers)

    def get_page(self, amt):
        """
        this function used to get page url from alrajhi provider
        @return: json response
        """
        track = uuid.uuid1().int.__str__()
        trandata = self.trandata(amt, track)
        data = self.body(trandata)
        response = self.post(data).json()

        if isinstance(response, list):
            response = response[0]

        if 'error' in response.keys():
            return None

        url = response.get('result', None)
        return {"url": url, "track": track}

    def get_data(self, trandata):
        """
        this functions used to extract data from trandata
        @param trandata: the encryption data
        @return: data
        """

        data = decrypt(trandata, self.resource, self.vector)
        return dict(parse.parse_qsl(parse.urlsplit(data).path))
