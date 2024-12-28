from django import template
from adminapp import models
register = template.Library()


@register.simple_tag
def get_all_cities():
    return models.City.activated.all()
