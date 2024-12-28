from django import template

from vendorapp import models

register = template.Library()


@register.simple_tag
def get_offers_types():
    return models.Offer.OfferTypeChoices.choices


