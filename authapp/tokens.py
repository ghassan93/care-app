import base64
import pyotp
from datetime import datetime
from django.conf import settings


class PasswordResetTokenGenerator(object):
    """
     This class returns the string needed to generate the key
    """
    secret = None

    def __init__(self):
        """
         The constructor function is used to set initial values for the secret code.
        """
        self.secret = self.secret or settings.SECRET_KEY

    def make_token(self, identifier):
        """
            Return a token that can be used once to do a password reset
            for the given user.
        """

        return self.__make_token_with_timestamp(identifier).now()

    def check_token(self, identifier, code):
        """

        @param identifier: The number to be verified
        @param code: The otp to check
        @return: verify
        """
        otp = self.__make_token_with_timestamp(identifier)
        return otp.verify(code)

    def __make_token_with_timestamp(self, identifier):
        """

        @param identifier: the identifier number for encryption
        @return: hash_string
        """

        key = str(identifier) + str(datetime.date(datetime.now())) + self.secret
        hash_string = base64.b32encode(key.encode())
        return pyotp.TOTP(hash_string, interval=settings.EXPIRY_TIME)


password_reset_token_generator = PasswordResetTokenGenerator()
