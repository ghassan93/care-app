from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.core.mail import EmailMultiAlternatives
from django import template
from allauth.account.utils import url_str_to_user_pk, user_pk_to_url_str
from allauth.utils import build_absolute_uri
from django.contrib.auth import get_user_model
from django.template import loader
from django.urls import reverse

from . import models

USER_MODEL = get_user_model()


def send_email(subject_template_name: str, email_template_name: str, context: dict, to_email: list, **kwargs):
    """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
    """

    try:
        subject = loader.render_to_string(subject_template_name, context)
    except template.TemplateDoesNotExist:
        subject = subject_template_name

    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    if not isinstance(to_email, list):
        to_email = [to_email]

    email_message = EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, to_email)
    if email_template_name is not None:
        html_email = loader.render_to_string(email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

    if 'file' in kwargs.keys():
        email_message.attach(
            kwargs.get('file_name', 'file'),
            kwargs['file'],
            kwargs.get('file_content', 'application/pdf')
        )

    return email_message.send()


def get_activate_url(request, user, url, code):
    """
    Constructs the email confirmation (activation) url.
    Note that if you have architected your system such that email
    confirmations are sent outside of the request context `request`
    can be `None` here.
    """
    uidb36 = user_pk_to_url_str(user)
    url = reverse(url, kwargs=dict(uidb36=uidb36, code=code))
    ret = build_absolute_uri(request, url)
    return ret


def get_user_by_b34(uidb36):
    """
    this function is used to get user form uidb36
    @param uidb36: the uidb36 value
    @return: object of User model or None
    """
    try:
        pk = url_str_to_user_pk(uidb36)
        return USER_MODEL.objects.get(pk=pk)
    except (ValueError, USER_MODEL.DoesNotExist, MultipleObjectsReturned):
        return None


def filter_user_objects_by_kwargs(**filters):
    """
    get user object that has is_deleted false and activated
    @param filters:  dict of filters values
    @return: object of User model or None
    """
    try:
        user = USER_MODEL.user_objects.get(**filters)

        if user.is_verified:
            return user

        raise Exception
    except (ValueError, USER_MODEL.DoesNotExist, MultipleObjectsReturned):
        return USER_MODEL.objects.none()


def filter_all_users_objects_by_kwargs(**filters):
    """
    get user object that has this filters
    @param filters:  dict of filters values
    @return: object of User model or None
    """
    try:
        return USER_MODEL.objects.get(**filters)
    except (ValueError, USER_MODEL.DoesNotExist, MultipleObjectsReturned):
        return USER_MODEL.objects.none()


def create_exponent_push_token(exponent_push_token, user):
    """
    create exponent push token object
    @param exponent_push_token: token of mobile
    @param user: the user object
    @return: object or None
    """
    try:
        models.ExponentPushToken.objects.create_or_update(exponent_push_token, user)
    except (ValueError, Exception):
        pass


def get_exponent_push_token(user):
    """
    get all exponent push token for user that pass for this function
    @param user: the user object
    @return: object or Empty list
    """
    try:
        return list(user.token.actives().values_list('receiver_token', flat=True))
    except (AttributeError,):
        return []
