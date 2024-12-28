from django import template
from .. import models

register = template.Library()


@register.simple_tag
def get_invoices_status():
    return models.Invoice.InvoiceStatusChoices.choices


@register.simple_tag
def get_invoices_types():
    return models.Invoice.InvoiceTypeChoices.choices
