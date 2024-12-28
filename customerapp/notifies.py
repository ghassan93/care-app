from django.contrib.auth import get_user_model
from notifications.signals import notify

from authapp import tasks as auth_task
from . import tasks
from .shortcut import send_email

USER_MODEL = get_user_model()


def send_create_order_notify(order, vendor, customer, service):
    """
    This function is used to send a notification to the user that his active
    email
    """
    user = vendor.vendor_user.first().user
    client = customer.user.get_full_name()
    service = service.name
    subject = 'تم حجز الخدمة {}'.format(service)
    message = 'قام العميل {} بطلب حجز الخدمة التي تحمل الاسم {}'.format(client, service)
    auth_task.send_push_message_task.delay(user.pk, message)
    send_email(user, subject, message)


def send_approval_order_notify(order):
    """
    This function is used to send a notification to the user that his active
    email
    """
    user = order.customer.user
    vendor = order.vendor
    subject = 'تمت الموافقة على الطلب الذي يحمل المعرف {}'.format(order.id)
    message = 'قام البائع {} بالموافقة على الطلب الذي يحمل الرقم {}'.format(vendor.name, order.id)
    auth_task.send_push_message_task.delay(user.pk, message)
    send_email(user, subject, message)


def send_disapproval_order_notify(order):
    """
    This function is used to send a notification to the user that his active
    email
    """
    user = order.customer.user
    vendor = order.vendor
    subject = 'تم رفض الطلب الذي يحمل المعرف {}'.format(order.id)
    message = 'قام البائع {} برفض الطلب الذي يحمل الرقم {}'.format(vendor.name, order.id)
    auth_task.send_push_message_task.delay(user.pk, message)
    send_email(user, subject, message)


def send_invoice_vendor_notify(order, invoice):
    """
    This function is used to send a notification to the user that his active
    email
    """

    customer = order.customer.user
    vendor = order.vendor.vendor_user.first().user
    subject = 'دفع قيمة الطلب {}'.format(order.pk)
    message = 'قام العميل {} بدفع مستحقات الطلب الذي يحمل الرقم {}'.format(
        customer.get_full_name(),
        order.pk
    )
    auth_task.send_push_message_task.delay(vendor.pk, message)
    send_email(vendor, subject, message)


def send_invoice_customer_notify(order, invoice):
    """
    This function is used to send a notification to the user that his active
    email
    """

    user = order.customer.user
    subject = 'تم دفع قيمة الطلب {}'.format(order.pk)
    message = 'قمت {} بدفع مستحقات الطلب الذي يحمل الرقم {}'.format(
        user.get_full_name(),
        order.pk
    )
    auth_task.send_push_message_task.delay(user.pk, message)
    tasks.send_invoice_mail_task.delay(subject, message, order.pk, invoice.pk, )


def payment_wallet_notify(user, invoice):
    """
    This function is used to notify admins is used created
    """
    message = 'قام العميل ({}) بدفع مبلغ ({}) عبر المحفظة.'.format(
        user.get_full_name(),
        invoice.get_total_value_display
    )
    admins = USER_MODEL.user_objects.admins()
    notify.send(user, recipient=admins, verb='Message', description=message)
    create_invoice_notify(user, invoice)


def payment_alrajhi_notify(user, invoice):
    """
    This function is used to notify admins is used created
    """
    message = 'قام العميل ({}) بدفع مبلغ ({}) عبر الراجحي.'.format(
        user.get_full_name(),
        invoice.get_total_value_display
    )
    admins = USER_MODEL.user_objects.admins()
    notify.send(user, recipient=admins, verb='Message', description=message)
    create_invoice_notify(user, invoice)


def payment_tamara_notify(user, invoice):
    """
    This function is used to notify admins is used created
    """
    message = 'قام العميل ({}) بدفع مبلغ ({}) عبر تمارا.'.format(
        user.get_full_name(),
        invoice.get_total_value_display
    )
    admins = USER_MODEL.user_objects.admins()
    notify.send(user, recipient=admins, verb='Message', description=message)
    create_invoice_notify(user, invoice)


def create_invoice_notify(user, invoice):
    """
    This function is used to notify admins is used created
    """
    message = 'تم إنشاء فاتورة جديدة تحمل الرقم ({})'.format(
        invoice.pk
    )
    admins = USER_MODEL.user_objects.admins()
    notify.send(user, recipient=admins, verb='Message', description=message)
