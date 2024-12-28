import datetime
from copy import deepcopy

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils import timezone


def current_datetime():
    """
    Return the default time zone as a time zone instance.
    This is the time zone defined by settings.TIME_ZONE.
    """
    return timezone.localtime(timezone.now())


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""

    if not start or not end:
        return None

        # If check time is not given, default to current UTC time
    if start < end:
        return start <= x <= end
    else:  # crosses midnight
        return x >= start or x <= end


def time2delta(time):
    """
    This function uses the transformation of an object of type timedelta.
    @param time: the input time
    @return: timedelta
    """

    return datetime.timedelta(hours=time.hour, minutes=time.minute)


def get_time(s):
    """
    this function used to covert str to time
    @param s: the str time format
    @return: time
    """
    return datetime.datetime.strptime(s, '%H:%M:%S').time()


def reserve(instance):
    """

    @param instance: the instance that has som attributes like start and end
    @return: boolean
    """
    return instance.reservation.filter(start=instance.start, end=instance.end, is_active=True).exists()


def create_range_date(instance, response, check_reserve=False):
    """
    This function is used to return range of dates
    @param instance: the instance that has som attributes like start and end
    @param response: the list of response
    @param check_reserve: The condition for check if reservation or not
    @return: response
    """

    step = instance.service.time
    start = instance.from_time
    end = instance.to_time
    while (end - start) >= step:
        instance = deepcopy(instance)
        temp = start + step
        instance.start = str(start)
        instance.end = str(temp)
        start = temp

        if not check_reserve or not reserve(instance):
            response.append(instance)

    return response


def get_range_date_list(instance, check_reserve=True):
    """
    @param instance: the instance that has som attributes like start and end
    @param check_reserve: The condition for check if reservation or not
    @return: list
    """

    response = []
    for data in create_range_date(instance, list(), check_reserve):
        response.append([get_time(data.start), get_time(data.end)])
    return response


def get_percent_value(total, percent):
    """
    This methode is used ro return percent value
    @return: value.
    """

    return (total * percent) / 100


def get_discount_value(price, discount_percent):
    """
    This methode is used ro return discount value
    @return: discount value
    """
    return get_percent_value(price, discount_percent)


def get_tax_value(total_before_tax, tax_percent):
    """
    This methode is used ro return tax value
    @return: discount value
    """
    return get_percent_value(total_before_tax, tax_percent)


def get_total_value_before_tax(price, discount_value=0):
    """
    This methode is used ro return total before tax
    @return: total before tax
    """
    return get_round_value(price - discount_value)


def get_total_value(total_before_tax, tax_value):
    """
    This methode is used ro return total
    @return: total.
    """
    return get_round_value(total_before_tax + tax_value)


def get_round_value(value):
    """
    This function used to return round value
    @return: round value
    """

    return round(value, 1)


def get_intcomma_display(value):
    """
    This function using to return intcomma value
    @param value: the number value
    @return:
    """
    return f"{intcomma(get_round_value(value), False)} {settings.DEFAULT_CURRENCY}"
