import json

import six
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str
from django_countries import settings
from django.utils.translation import gettext_lazy as _
from django.forms import ModelMultipleChoiceField, ModelChoiceField
from rest_framework import serializers
from rest_framework.relations import RelatedField
from taggit.serializers import TagList as taggit_TagList, TaggitSerializer as taggit_TaggitSerializer


class ModelMultipleSlugChoiceField(ModelMultipleChoiceField):
    """A ChoiceField whose choices are a model QuerySet."""

    def __init__(self, *args, **kwargs):
        kwargs['to_field_name'] = 'slug'
        super(ModelMultipleSlugChoiceField, self).__init__(*args, **kwargs)


class ModelSlugChoiceField(ModelChoiceField):
    """A ChoiceField whose choices are a model QuerySet."""

    def __init__(self, *args, **kwargs):
        kwargs['to_field_name'] = 'slug'
        super(ModelSlugChoiceField, self).__init__(*args, **kwargs)


class PasswordField(serializers.CharField):
    """
    This field is used to enter and verify the password
    """

    def __init__(self, **kwargs):
        # self.validators = [validate_password]
        self.max_length = settings.ACCOUNT_PASSWORD_MAX_LENGTH
        self.min_length = settings.ACCOUNT_PASSWORD_MIN_LENGTH
        self.write_only = True
        self.style = {'input_type': 'password'}
        super(PasswordField, self).__init__(**kwargs)


class EmailField(serializers.EmailField):
    def __init__(self, **kwargs):
        kwargs['style'] = {
            'input_type': 'email',
            "input_placeholder": _("عنوان البريد الإلكتروني"),
            "input_autocomplete": "email",
        }
        kwargs['required'] = kwargs.pop('required', settings.ACCOUNT_EMAIL_REQUIRED)
        kwargs['max_length'] = kwargs.pop('max_length', settings.ACCOUNT_EMAIL_MAX_LENGTH)
        super(EmailField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        # We're lenient with allowing basic numerics to be coerced into strings,
        # but other types should fail. Eg. unclear if booleans should represent as `true` or `True`,
        # and composites such as lists are likely user error.
        value = super(EmailField, self).to_internal_value(data)
        return value.lower()


class TagList(taggit_TagList):
    def __str__(self):
        if self.pretty_print:
            return json.dumps(
                self, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
        else:
            return json.dumps(self, ensure_ascii=False)


class TaggitSerializer(taggit_TaggitSerializer):

    def _pop_tags(self, validated_data):
        to_be_tagged = {}

        for key in self.fields.keys():
            field = self.fields[key]
            if isinstance(field, TagListSerializerField):
                if key in validated_data:
                    to_be_tagged[key] = validated_data.pop(key)

        return to_be_tagged, validated_data


class TagListSerializerField(RelatedField):
    default_error_messages = {
        'not_a_list': _('من المتوقع الحصول على قائمة لكن تم الحصول على "{input_type}"'),
        'not_a_str': _('يجب أن تكون كافة عناصر القائمة من نوع سلسلة.'),
        'does_not_exist': _('عنصر ب {slug_name}={value} غير موجود.')
    }
    child = serializers.CharField()

    order_by = None

    def __init__(self, slug_field=None, **kwargs):
        assert slug_field is not None, 'The `slug_field` argument is required.'
        self.slug_field = slug_field
        pretty_print = kwargs.pop("pretty_print", True)
        style = kwargs.pop("style", {})
        kwargs["style"] = {'base_template': 'textarea.html'}
        kwargs["style"].update(style)

        super(TagListSerializerField, self).__init__(**kwargs)

        self.pretty_print = pretty_print

    def to_internal_value(self, value):
        tags = []

        if isinstance(value, six.string_types):
            if not value:
                value = "[]"
            try:
                value = json.loads(value)
            except ValueError:
                value = value.split(',')

        if not isinstance(value, list):
            self.fail('not_a_list', input_type=type(value).__name__)

        queryset = self.get_queryset()
        for s in value:
            if not isinstance(s, six.string_types):
                self.fail('not_a_str')
            self.child.run_validation(s)
            try:
                tage = queryset.get(**{self.slug_field: s})
            except ObjectDoesNotExist:
                self.fail('does_not_exist', slug_name=self.slug_field, value=smart_str(s))
            tags.append(s)
        return tags

    def to_representation(self, value):

        if not isinstance(value, taggit_TagList):
            if not isinstance(value, list):
                if self.order_by:
                    tags = value.all().order_by(*self.order_by)
                else:
                    tags = value.all()
                value = [tag.name for tag in tags]

            value = TagList(value, pretty_print=False)
        return value


class RecursiveField(serializers.Serializer):
    """
    This class is used to deal with interrelationships
    """
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data
