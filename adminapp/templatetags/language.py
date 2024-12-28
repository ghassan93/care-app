from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def get_languages():
    return settings.LANGUAGES


@register.simple_tag
def get_language_code():
    return settings.LANGUAGE_CODE
