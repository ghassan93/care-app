from django import template

from vendorapp import models

register = template.Library()


@register.simple_tag
def get_vendors_types():
    return models.VendorTypeChoice.choices


@register.simple_tag
def get_payments_types():
    return models.Vendor.PaymentTypeChoices.choices


@register.simple_tag
def get_places_types():
    return models.Vendor.PlaceChoices.choices


@register.simple_tag
def get_allowed_types():
    return models.Vendor.AllowedChoices.choices


@register.simple_tag
def get_hours_choices():
    return models.hours_choices()


@register.simple_tag
def get_minutes_choices():
    return models.minutes_choices()
