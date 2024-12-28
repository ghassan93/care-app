import pytz
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.utils.functional import SimpleLazyObject

from rest_framework.request import Request
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


def get_user_jwt(request):
    """
    Replacement for django session auth get_user & auth.get_user for
     JSON Web Token authentication. Inspects the token for the user_id,
     attempts to get that user from the DB & assigns the user on the
     request object. Otherwise it defaults to AnonymousUser.
    This will work with existing decorators like LoginRequired, whereas
    the standard restframework_jwt auth only works at the view level
    forcing all authenticated users to appear as AnonymousUser ;)
    Returns: instance of user object or AnonymousUser object
    """
    user = None
    try:
        user_jwt = JSONWebTokenAuthentication().authenticate(Request(request))
        if user_jwt is not None:
            # store the first part from the tuple (user, obj)
            user = user_jwt[0]
    except (Exception,):
        pass

    return user or AnonymousUser()


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        Returned None for continue request
        """
        if request.user.is_anonymous:
            request.user = SimpleLazyObject(lambda: get_user_jwt(request))
        if request.user.is_authenticated:
            tzname = request.user.profile.timezone
            if tzname:
                timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
