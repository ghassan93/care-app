from django import template

from vendorapp import models

register = template.Library()


@register.simple_tag
def get_services_types():
    return models.Service.ServiceTypeChoice.choices


@register.simple_tag
def get_services_places():
    return models.Service.PlaceChoices.choices


@register.simple_tag
def get_services_schedules():
    return models.Service.ScheduleTypeChoices.choices
