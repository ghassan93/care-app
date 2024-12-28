from django.db.models.signals import pre_save
from django.dispatch import receiver, Signal

from utils.decorators import disable_for_fixture
from utils.slug import unique_slug_generator
from . import models, notifies

"""
 ============================================================== 
     Django Signals for Notification
 ============================================================== 
"""
create_offer_code = Signal()
deposit_wallet = Signal()
withdraw_wallet = Signal()


@receiver(create_offer_code)
def receiver_create_offer_code(sender, request, user, **kwargs):
    """

    @param sender:
    @param request:
    @param user:
    @param kwargs:
    """
    notifies.send_active_code_notify()
    notifies.send_active_code_done_notify(user)


@receiver(deposit_wallet)
def receiver_deposit_wallet(sender, user, amount, **kwargs):
    """

    @param sender:
    @param user:
    @param amount:
    @param kwargs:
    """
    notifies.send_deposit_wallet_notify(user, amount)


@receiver(withdraw_wallet)
def receiver_withdraw_wallet(sender, user, amount, **kwargs):
    """

    @param sender:
    @param user:
    @param amount:
    @param kwargs:
    """
    notifies.send_withdraw_wallet_notify(user, amount)


"""
 ============================================================== 
     Django Signals for DB
 ============================================================== 
"""


@receiver(pre_save, sender=models.City)
@disable_for_fixture
def receiver_create_slug(sender, instance, *args, **kwargs):
    """

    @param sender:
    @param instance:
    @param args:
    @param kwargs:
    """
    if not instance.slug:
        instance.slug = unique_slug_generator(instance, 'code')


@receiver(pre_save, sender=models.Policies)
@disable_for_fixture
def receiver_create_slug(sender, instance, *args, **kwargs):
    """

    @param sender:
    @param instance:
    @param args:
    @param kwargs:
    """
    if not instance.slug:
        instance.slug = unique_slug_generator(instance, 'title')
