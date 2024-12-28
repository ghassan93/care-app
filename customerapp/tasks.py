from celery import shared_task
from . import models
from .shortcut import render_invoice_pdf, SUBJECT, TEMPLATE


@shared_task
def send_invoice_mail_task(subject, message, order_id, invoice_id):
    """
       Send a django.core.mail.EmailMultiAlternatives to `to_email`.
    """

    from authapp.shortcut import send_email

    invoice = models.Invoice.verified_objects.get(pk=invoice_id)
    order = models.Order.verified_objects.get(pk=order_id)
    user = order.customer.user
    pdf = render_invoice_pdf(invoice)
    ctx = {
        'name': user.get_full_name(),
        'subject': subject,
        'message': message,
    }

    send_email(SUBJECT, TEMPLATE, ctx, user.email, file_name=f'Invoice Order No {order.pk}.pdf', file=pdf)
