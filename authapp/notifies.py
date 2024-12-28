from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from notifications.signals import notify

from .shortcut import get_activate_url
from . import tasks, tokens

USER_MODEL = get_user_model()


def send_otp_to_email_notify(subject, template, request, user, activate_url_name, method, **ctx):
    """
    This function is used to send email notifications containing a special
    code that the user uses to activate something
    like send reset password or activate email.
    """

    current_site = get_current_site(request)
    code = tokens.password_reset_token_generator.make_token(user.email)
    activate_url = get_activate_url(
        request, user, activate_url_name, code
    ) if activate_url_name and user.is_admin else ''

    ctx.update({
        'name': user.get_full_name(),
        'email': user.email,
        'activate_url': activate_url,
        'site_domain': current_site.domain,
        'site_name': current_site.name,
        'code': code,
        'role': user.role,
        'method': method
    })

    tasks.send_mail_task.delay(subject, template, ctx, user.email)


def send_email_confirmation_notify(request, user, method):
    subject = 'care/authapp/email/auth-email-confirmation-signup-subject.txt'
    template = 'care/authapp/email/auth-email-confirmation-signup-message.html'
    send_otp_to_email_notify(subject, template, request, user, '', method)


def send_email_reset_password_notify(request, user):
    subject = 'care/authapp/email/auth-password-reset-key-subject.txt'
    template = 'care/authapp/email/auth-password-reset-key-message.html'
    send_otp_to_email_notify(subject, template, request, user, 'auth:reset_password_key_view', 'reset-password')


def send_reset_password_done_notify(user):
    """
    This function is used to send a notification to the user that his password
    has been successfully restored
    """

    message = 'تمت استعادة كلمة المرور بنجاح.'
    tasks.send_push_message_task.delay(user.pk, message)


def send_activate_email_notify(user):
    """
    This function is used to send a notification to the user that his active
    email
    """

    message = 'تم تفعيل البريد الإلكتروني الخاص بحسابك.'
    tasks.send_push_message_task.delay(user.pk, message)


def send_email_changed_notify(user, from_email_address, to_email_address):
    """
    This function is used to send a notification to the user that his active
    email
    """

    message = f'تم استبدال بريدك الإلكتروني من {from_email_address}  بالبريد التالي  {to_email_address}.'
    tasks.send_push_message_task.delay(user.pk, message)


def send_password_changed_notify(user):
    """
    This function is used to send a notification to the user that his active
    email
    """

    message = 'تم تعديل كلمة المرور الخاصة بحسابك.'
    tasks.send_push_message_task.delay(user.pk, message)


def user_signed_up_notify(new_user):
    """
    This function is used to notify admins is used created
    """
    message = 'تم تسجيل مستخدم جديد يحمل الاسم ({}) من نوع ({}).'.format(
        new_user.get_full_name(),
        new_user.get_role_display()
    )
    admins = USER_MODEL.user_objects.admins()
    notify.send(new_user, recipient=admins, verb='Message', description=message)
