from django.contrib.auth.validators import ASCIIUsernameValidator as ValidatorsASCIIUsernameValidator
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.utils.representation import smart_repr
from rest_framework.validators import UniqueTogetherValidator as ValidatorsUniqueTogetherValidator, qs_exists


class ASCIIUsernameValidator(ValidatorsASCIIUsernameValidator):
    regex = r'^(?=.*[A-Za-z])[\w\d#$]{5,30}$'
    message = _(
        "عذرًا ، يجب أن تتضمن أسماء المستخدمين المكونة من 6 أحرف أو أكثر "
        "حرفًا أبجديًا واحدًا (a-z) او أرقام او الرموز $ #"
    )


class UniqueTogetherValidator(ValidatorsUniqueTogetherValidator):
    def __call__(self, attrs, serializer):
        self.enforce_required_fields(attrs, serializer)
        queryset = self.queryset
        queryset = self.filter_queryset(attrs, queryset, serializer)
        queryset = self.exclude_current_instance(attrs, queryset, serializer.instance)

        # Ignore validation if any field is None
        checked_values = [
            value for field, value in attrs.items() if field in self.fields
        ]
        if None not in checked_values and qs_exists(queryset):
            raise self.message


class RequiredTogetherValidator:
    """
    Validator that corresponds to `unique_together = (...)` on a model class.

    Should be applied to the serializer class, not to an individual field.
    """

    message = _('يجب إدخال قيمة صحيحة الى هذه الحقول {field_names}.')
    missing_message = _('هذا الحقل مطلوب')
    requires_context = True

    def __init__(self, fields, message=None):
        self.fields = fields
        self.message = message or self.message

    def enforce_required_fields(self, attrs, serializer):
        """
        The `UniqueTogetherValidator` always forces an implied 'required'
        state on the fields it applies to.
        """

        if serializer.instance is not None:
            return

        missing_items = {
            field_name: self.missing_message
            for field_name in self.fields
            if serializer.fields[field_name].source not in attrs
        }
        if missing_items:
            raise ValidationError(missing_items, code='required')

    def get_attrs(self, attrs, serializer):
        """
        Filter the queryset to all instances matching the given attributes.
        """
        # field names => field sources
        sources = [
            serializer.fields[field_name].source
            for field_name in self.fields
        ]

        # If this is an update, then any unprovided field should
        # have it's value set based on the existing instance attribute.
        if serializer.instance is not None:
            for source in sources:
                if source not in attrs:
                    attrs[source] = getattr(serializer.instance, source)

        return attrs

    def __call__(self, attrs, serializer):
        self.enforce_required_fields(attrs, serializer)
        attrs = self.get_attrs(attrs, serializer)

        checked_values = [
            value for field, value in attrs.items() if field in self.fields and value
        ]

        if not checked_values:
            field_names = ', '.join(self.fields)
            message = self.message.format(field_names=field_names)
            raise ValidationError(message, code='required')

    def __repr__(self):
        return '<%s(fields=%s)>' % (
            self.__class__.__name__,
            smart_repr(self.fields)
        )


alpha = r'^[a-zA-Z_-]+$'
alphanumeric = r'^([a-zA-Z]+|[a-zA-Z]+\d+|\d+[a-zA-Z]+)+$'
