from django import template
from .. import models
register = template.Library()


@register.simple_tag
def get_all_genders():
    return models.Profile.GenderChoices.choices
