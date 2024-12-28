import random
import string

from django.utils.functional import keep_lazy_text
from django.utils.text import slugify as django_slugify


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@keep_lazy_text
def slugify(value):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = django_slugify(value, allow_unicode=True)
    return value or random_string_generator(size=4)


def unique_slug_generator(instance, attributes=None, new_slug=None, ):
    slug = slugify(new_slug if new_slug else getattr(instance, attributes))
    klass = instance.__class__
    max_length = klass._meta.get_field('slug').max_length
    slug = slug[:max_length]
    qs_exists = klass.objects.filter(slug=slug).exists()

    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug[:max_length - 5],
            randstr=random_string_generator(size=4)
        )

        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def model_unique_slug_generator(klass, value=None, attribute='name', new_slug=None, ):
    slug = slugify(new_slug if new_slug else value, allow_unicode=True)
    max_length = klass._meta.get_field(attribute).max_length
    slug = slug[:max_length]
    qs_exists = klass.objects.filter(**{attribute: slug}).exists()

    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug[:max_length - 5], randstr=random_string_generator(size=4))
        return model_unique_slug_generator(klass, attribute=attribute, new_slug=new_slug)
    return slug
