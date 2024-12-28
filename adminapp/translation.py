from modeltranslation.translator import register, TranslationOptions
from .models import Policies


@register(Policies)
class PortTranslationOptions(TranslationOptions):
    fields = ('content',)
