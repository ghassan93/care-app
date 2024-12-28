from django.db.models.signals import pre_save
from django.dispatch import receiver, Signal

from utils.decorators import disable_for_fixture
from utils.slug import unique_slug_generator
from . import models, notifies

create_vendor = Signal()
create_withdraw_request = Signal()

"""
 ============================================================== 
     Django Signals for Notification
 ============================================================== 
"""


@receiver(create_withdraw_request)
def receiver_create_withdraw_request(sender, user, amount, **kwargs):
    """

    @param sender:
    @param user:
    @param amount:
    @param kwargs:
    """
    notifies.send_create_withdraw_request_notify(user, amount)


"""
 ============================================================== 
     Django Signals for DB
 ============================================================== 
"""


@receiver(create_vendor)
@disable_for_fixture
def receiver_create_slug(sender, vendor, *args, **kwargs):
    """

    @param sender:
    @param vendor:
    @param args:
    @param kwargs:
    """
    vendor.slug = unique_slug_generator(vendor, 'name')
    vendor.save()


@receiver(create_vendor)
@disable_for_fixture
def receiver_create_vendor(sender, vendor, user, **kwargs):
    """

    @param sender:
    @param vendor:
    @param user:
    @param kwargs:
    """

    return models.VendorUser.objects.create(user=user, vendor=vendor, is_manager=True)


@receiver(pre_save, sender=models.Service)
@disable_for_fixture
def receiver_create_slug(sender, instance, *args, **kwargs):
    """

    @param sender:
    @param instance:
    @param args:
    @param kwargs:
    """
    if not instance.slug:
        instance.slug = unique_slug_generator(instance, 'name')
