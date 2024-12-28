import logging
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from utils.decorators import disable_for_fixture
from . import models, notifies, shortcut

logger = logging.getLogger(__name__)

"""
 ============================================================== 
     Django Signals for Notification
 ============================================================== 
"""
order_create = Signal()
order_approval = Signal()
order_disapproval = Signal()
wallet_payment_success = Signal()
alrajhi_payment_success = Signal()
alrajhi_with_wallet_payment_success = Signal()
tamara_payment_success = Signal()


@receiver(order_create)
def receiver_order_create(sender, order, vendor, customer, service, **kwargs):
    """
    @param sender:
    @param order:
    @param vendor:
    @param customer:
    @param service:
    @param kwargs:
    """
    notifies.send_create_order_notify(order, vendor, customer, service)


@receiver(order_approval)
def receiver_order_approval(sender, order, **kwargs):
    """

    @param sender:
    @param order:
    @param kwargs:
    """

    for order_item in order.order_item.all():
        if hasattr(order_item, 'reservation'):
            order_item.reservation.activate()

    notifies.send_approval_order_notify(order)


@receiver(order_disapproval)
def receiver_order_disapproval(sender, order, **kwargs):
    """

    @param sender:
    @param order:
    @param kwargs:
    """

    for order_item in order.order_item.all():
        if hasattr(order_item, 'reservation'):
            order_item.reservation.disabled()
    notifies.send_disapproval_order_notify(order)


@receiver(wallet_payment_success)
def receiver_wallet_payment_success(sender, order, invoice, **kwargs):
    """
    @param sender:
    @param order:
    @param invoice:
    @return:
    """

    notifies.send_invoice_vendor_notify(order, invoice)
    notifies.send_invoice_customer_notify(order, invoice)
    notifies.payment_wallet_notify(order.customer.user, invoice)


@receiver(alrajhi_payment_success)
def receiver_alrajhi_payment_success(sender, order, invoice, **kwargs):
    """
    @param sender:
    @param order:
    @param invoice:
    @return:
    """

    notifies.send_invoice_vendor_notify(order, invoice)
    notifies.send_invoice_customer_notify(order, invoice)
    notifies.payment_alrajhi_notify(order.customer.user, invoice)


@receiver(tamara_payment_success)
def receiver_tamara_payment_success(sender, order, invoice, **kwargs):
    """
    @param sender:
    @param order:
    @param invoice:
    @return:
    """

    notifies.send_invoice_vendor_notify(order, invoice)
    notifies.send_invoice_customer_notify(order, invoice)
    notifies.payment_tamara_notify(order.customer.user, invoice)


"""
 ============================================================== 
     Django Signals for DB
 ============================================================== 
"""


@receiver(post_save, sender=get_user_model())
@disable_for_fixture
def receiver_create_user(sender, instance, created, **kwargs):
    """

    @param sender:
    @param instance:
    @param created:
    @param kwargs:
    """
    if created and instance.is_customer:
        models.Customer.objects.create(user=instance)


@receiver(post_save, sender=models.Customer)
@disable_for_fixture
def receiver_create_customer(sender, instance, created, **kwargs):
    """

    @param sender:
    @param instance:
    @param created:
    @param kwargs:
    """
    if created:
        models.Wallet.objects.create(customer=instance)


@receiver(post_save, sender=models.Invoice)
@disable_for_fixture
def receiver_create_invoice(sender, instance, created, **kwargs):
    """

    @param sender:
    @param instance:
    @param created:
    @param kwargs:
    """
    if created:
        offer = instance.offer
        if offer is not None:
            offer.users.add(instance.order.customer.user)


@receiver(post_save, sender=models.OrderItem)
@disable_for_fixture
def receiver_create_order_item(sender, instance, created, **kwargs):
    """

    @param sender:
    @param instance:
    @param created:
    @param kwargs:
    """

    availability = instance.availability

    if not created or not availability:
        return

    models.Reservation.objects.create(
        order_item=instance, availability=availability, date=instance.date,
        start=instance.start, end=instance.end
    )


@receiver(post_save, sender=models.Payment)
@disable_for_fixture
def receiver_create_payment(sender, instance, created, **kwargs):
    """

    @param sender:
    @param instance:
    @param created:
    @param kwargs:
    """

    if not created or not instance:
        return

    try:
        customer = instance.invoice.order.customer
        total_paid = instance.payment_object.amount
        back_cash_value = shortcut.get_back_cash_value(total_paid)
        customer.wallet.deposit(back_cash_value, customer.user)
    except AttributeError as e:
        logger.error(e)
