import logging
import rollbar
from django.contrib.auth import get_user_model
from celery import shared_task
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from notifications.signals import notify
from requests.exceptions import ConnectionError, HTTPError
from authapp.shortcut import (
    send_email,
    filter_user_objects_by_kwargs,
    get_exponent_push_token,

)

logger = logging.getLogger(__name__)

USER_MODEL = get_user_model()


@shared_task
def send_mail_task(subject_template_name: str, email_template_name: str, context: dict, to_email: list, **kwargs):
    """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    return send_email(subject_template_name, email_template_name, context, to_email, **kwargs)


@shared_task(bind=True)
def send_push_message_task(self, recipients, message: str, extra: dict = None):
    """
    This function is used to send a notification to the user that his password
    has been successfully restored

    This function is used to send notifications to the application
    associated with the user through the Expo framework
    @param self
    @param recipients: the users primary key
    @param message: the message
    @param extra: the extra data
    """

    if isinstance(recipients, list):
        users_list_data = [filter_user_objects_by_kwargs(pk=pk) for pk in recipients]
    else:
        users_list_data = [filter_user_objects_by_kwargs(pk=recipients)]

    for user in users_list_data:
        tokens_list_data = get_exponent_push_token(user)
        for token in tokens_list_data:
            try:
                response = PushClient().publish(PushMessage(to=token, body=message, data=extra))
            except PushServerError as exc:
                # Encountered some likely formatting/validation error.
                rollbar.report_exc_info(
                    extra_data={
                        'recipients': recipients,
                        'message': message,
                        'extra': extra,
                        'errors': exc.errors,
                        'response_data': exc.response_data,
                    })
                raise
            except (ConnectionError, HTTPError) as exc:
                # Encountered some Connection or HTTP error - retry a few times in
                # case it is transient.
                rollbar.report_exc_info(
                    extra_data={
                        'recipients': recipients,
                        'message': message,
                        'extra': extra
                    }
                )
                logger.error('exception raised, ConnectionError')
                raise self.retry(exc=exc, countdown=5)

            try:
                # We got a response back, but we don't know whether it's an error yet.
                # This call raises errors so we can handle them with normal exception
                # flows.
                token = response.push_message.to
                response.validate_response()
            except DeviceNotRegisteredError:
                # Mark the push token as inactive
                from authapp.models import ExponentPushToken
                ExponentPushToken.objects.filter(receiver_token=token).update(is_active=False)
            except PushTicketError as exc:
                # Encountered some other per-notification error.
                rollbar.report_exc_info(
                    extra_data={
                        'recipients': recipients,
                        'message': message,
                        'extra': extra,
                        'push_response': exc.push_response._asdict(),
                    })
                logger.error('exception raised, PushTicketError')
                raise self.retry(exc=exc, countdown=5)
        notify.send(user, recipient=user, verb='Message', description=message)
