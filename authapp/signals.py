from allauth.account.utils import setup_user_email
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver, Signal

from utils.decorators import disable_for_fixture
from utils.slug import unique_slug_generator
from . import models, notifies

"""
 ============================================================== 
     Django Signals for Notification
 ============================================================== 
"""
user_signed_up = Signal()
resend_activate_email = Signal()
activate_email = Signal()
user_logged_in = Signal()
password_reset_send = Signal()
password_reset_done = Signal()
password_changed = Signal()
email_changed = Signal()

USER_MODEL = get_user_model()


@receiver(user_signed_up)
def receiver_user_signed_up(sender, request, user, **kwargs):
    """

    @param sender:
    @param request:
    @param user:
    @param kwargs:
    """
    setup_user_email(request, user, [])
    notifies.send_email_confirmation_notify(request, user, 'signup')
    notifies.user_signed_up_notify(user)


@receiver(resend_activate_email)
def receiver_resend_activate_email(sender, request, user, **kwargs):
    """

    @param sender:
    @param request:
    @param user:
    @param kwargs:
    """
    notifies.send_email_confirmation_notify(request, user, 'resend-active-email')


@receiver(activate_email)
def receiver_activate_email(sender, user, **kwargs):
    """

    @param sender:
    @param user:
    @param kwargs:
    """
    notifies.send_activate_email_notify(user)


@receiver(password_reset_send)
def receiver_password_reset_send(sender, request, user, **kwargs):
    """

    @param sender:
    @param request:
    @param user:
    @param kwargs:
    """
    notifies.send_email_reset_password_notify(request, user)


@receiver(password_reset_done)
def receiver_password_reset_done(sender, user, **kwargs):
    """

    @param sender:
    @param user:
    @param kwargs:
    """
    notifies.send_reset_password_done_notify(user)


@receiver(email_changed)
def receiver_email_changed(sender, request, user, from_email_address, to_email_address, **kwargs):
    """

    @param sender:
    @param request:
    @param user:
    @param from_email_address:
    @param to_email_address:
    @param kwargs:
    """

    notifies.send_email_confirmation_notify(request, user, 'change-email')
    notifies.send_email_changed_notify(user, from_email_address, to_email_address)


@receiver(password_changed)
def receiver_password_changed(sender, user, **kwargs):
    """

    @param sender:
    @param user:
    @param kwargs:
    """

    notifies.send_password_changed_notify(user)


"""
 ============================================================== 
     Django Signals for DB
 ============================================================== 
"""


@receiver(pre_save, sender=USER_MODEL)
@disable_for_fixture
def receiver_create_slug(sender, instance, *args, **kwargs):
    """

    @param sender:
    @param instance:
    @param args:
    @param kwargs:
    """
    if not instance.slug:
        instance.slug = unique_slug_generator(instance, 'username')


@receiver(post_save, sender=USER_MODEL)
@disable_for_fixture
def receiver_create_profile(sender, instance, created, **kwargs):
    """

    @param sender:
    @param instance:
    @param created:
    @param kwargs:
    """
    if created:
        models.Profile.objects.create(user=instance)
