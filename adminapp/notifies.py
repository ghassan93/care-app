from django.conf import settings
from django.contrib.auth import get_user_model
from notifications.signals import notify

from authapp import tokens, tasks

USER_MODEL = get_user_model()


def send_active_code_notify():
    subject = 'care/authapp/email/auth-email-active-code-subject.txt'
    template = 'care/authapp/email/auth-email-active-code-message.html'
    code = tokens.password_reset_token_generator.make_token(settings.SECRET_KEY)
    admins = [u[0] for u in USER_MODEL.user_objects.admins().values_list('email')]
    context = {'code': code}
    tasks.send_mail_task.delay(subject, template, context, admins)


def send_active_code_done_notify(user):
    """
    This function is used to send a notification to the user that his password
    has been successfully restored
    """

    message = 'تم انتشاء كود للخصم من قبل المستخدم ({}).'.format(user.get_full_name())
    admins = USER_MODEL.user_objects.admins()
    notify.send(user, recipient=admins, verb='Message', description=message)


def send_deposit_wallet_notify(user, amount):
    """
    This function is used to send a notification to the user that his password
    has been successfully restored
    """

    message = 'تم إيداع رصيد في محفظة المستخدم ({}) بقيمة ({} {})'.format(
        user.get_full_name(),
        amount,
        settings.DEFAULT_CURRENCY

    )
    admins = USER_MODEL.user_objects.admins()
    notify.send(user, recipient=admins, verb='Message', description=message)


def send_withdraw_wallet_notify(user, amount):
    """
    This function is used to send a notification to the user that his password
    has been successfully restored
    """

    message = 'تم سحب رصيد من محفظة المستخدم ({}) بقيمة ({} {})'.format(
        user.get_full_name(),
        amount,
        settings.DEFAULT_CURRENCY

    )
    admins = USER_MODEL.user_objects.admins()
    notify.send(user, recipient=admins, verb='Message', description=message)
