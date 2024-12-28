from django.contrib.auth import get_user_model
from notifications.signals import notify

USER_MODEL = get_user_model()


def send_create_withdraw_request_notify(user, amount):
    """
    This function is used to send a notification to the user that his password
    has been successfully restored
    """

    message = 'قام المستخدم ({}) التابع للبائع {} بطلب مبلغ {} ريال.'.format(
        user.get_full_name(),
        user.vendor_user.vendor.name,
        amount
    )
    admins = USER_MODEL.user_objects.admins()
    notify.send(user, recipient=admins, verb='Message', description=message)
