from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler


def jwt_response_payload_handler(user=None):
    """
    Returns the response data for both the login and refresh views.
    Override to return a custom response such as including the
    serialized representation of the User.

    Example:

    def jwt_response_payload_handler(token, user=None, request=None):
        return {
            'token': token,
            'user': UserSerializer(user, context={'request': request}).data
        }

    """

    token = jwt_encode_handler(jwt_payload_handler(user))

    response = {
        'token': token,
        'fullname': user.get_full_name(),
        'username': user.username,
        'email': user.email,
        'phone': user.phonenumber.as_e164,
        'role_name': user.get_role_display(),
        'role': user.role,

    }

    if user.is_vendor:
        response.update({'vendor': {
            'name': user.vendor_user.vendor.name,
            'vendor_type': user.vendor_user.vendor.vendor_type
        }})

    return response
