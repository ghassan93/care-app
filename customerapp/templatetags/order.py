from django import template
from .. import models
register = template.Library()


@register.simple_tag
def get_status_types():
    return models.Order.OrderStatusChoices.choices
