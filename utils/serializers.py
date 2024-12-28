from django.http import QueryDict

from rest_framework import serializers


class Serializer(serializers.Serializer):
    """
    This class is base class for Serializer.
    """

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(Serializer, self).__init__(*args, **kwargs)
        self.read_only_fields = []

    def set_source_attrs(self, field_name, source):
        """
        this function used to set source_attrs value
        :param field_name: the name  field
        :param source: the source value
        """

        field = self.fields.get(field_name, None)

        if field is None:
            return

        field.source_attrs = source.split('.')

    def get_field_value(self, filed_name):
        """
        this function is used to get field value
        :param filed_name: the name of field
        :return: value
        """
        field = self.fields.get(filed_name, None)
        initial_data = getattr(self, 'initial_data', None)

        if not field:
            return None

        if isinstance(field, serializers.HiddenField):
            return field.get_default()

        if isinstance(initial_data, QueryDict) and filed_name in initial_data.keys():
            primitive_value = field.get_value(initial_data)
            if primitive_value:
                return field.run_validation(primitive_value)

        return getattr(self.instance, filed_name, None)

    def get_fields(self):
        """
        Return the dict of field names -> field instances that should be
        used for `self.fields` when instantiating the serializer.
        """
        fields = super().get_fields()
        for field in fields:
            if field in self.read_only_fields:
                fields[field].read_only = True
        return fields

    def get_method_action(self):
        """
        this function used to return method action
        :return: method action
        """
        method = self.context.get('view', None)
        return getattr(method, 'action', 'null')

    def is_post_action(self):
        """
        this function check if the action is post
        :return: Boolean
        """
        action = self.get_method_action()
        return action in ['create']

    def is_put_action(self):
        """
        this function check if the action is put
        :return: Boolean
        """
        action = self.get_method_action()
        return action in ['update', 'partial_update']


class FormSerializer(Serializer):
    """
    This class is base class for Form Serializer.
    """

    form_class = None

    form = None

    def get_form_class(self, attrs):
        """
        This function is used to initialize the form data
        """
        return self.form_class(data=attrs)

    def validate(self, attrs):
        """

        @param attrs:
        @return:
        """
        self.form = self.get_form_class(attrs=attrs)
        if not self.form.is_valid():
            raise serializers.ValidationError(self.form.errors)
        return attrs

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        return self.form.save()


class GenericModelSerializer(serializers.Serializer):
    """
    This class is used to deal with public relations through the process of creation,
    updating, presentation, and others.
    It collects a set of common functions between the classes and puts them in this
    common class
    """

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(GenericModelSerializer, self).__init__(*args, **kwargs)
        self.generic_field = 'generic'

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        object_id = self.context['object_id']

        instance = getattr(object_id, self.generic_field).create_generic_object(**validated_data)
        return instance


class ModelSerializer(Serializer, serializers.ModelSerializer):
    """
    This class is base class for Model Serializer.
    """

    class Meta:
        abstract = True
