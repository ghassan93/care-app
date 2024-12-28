from django.contrib.auth import get_user_model
from phonenumber_field.phonenumber import to_python

USER_MODEL = get_user_model()


class AuthenticationBackend(object):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:

            if '@' in username:
                kwargs.update({'email': username.lower()})

            elif to_python(username).is_valid():
                kwargs.update({'phonenumber': username})

            else:
                kwargs.update({'username': username})

            user = USER_MODEL.user_objects.get(**kwargs)

            if user.check_password(password) and user.is_verified:
                return user

        except (USER_MODEL.DoesNotExist, Exception):
            return None

    def get_user(self, user_id):
        try:
            return USER_MODEL.objects.get(pk=user_id)
        except USER_MODEL.DoesNotExist:
            return None
