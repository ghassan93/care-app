from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework import serializers
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from adminapp import models as admin_models
from . import serializers as utils_serializers


class GenericRelationshipModelMixin:

    def get_object(self):
        """
        This function is used to return the value of a specified object by
        either the object number or the token associated with the object
        """
        return {}

    def create_generic_object(self, request, serializer, message):
        """
        This function is used to add an object that has a general relationship
        with another object
        """

        instance = self.get_object()
        serializer = serializer(
            context={'request': request, 'object_id': instance}, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': message}, status=status.HTTP_201_CREATED)

    def delete_generic_object(self, model, pk, reverse_relation):
        """
        This function is used to delete an object that has a general relationship
        with another object
        """

        instance = self.get_object()
        generic_object = get_object_or_404(
            model, pk=pk, object_id=getattr(instance, 'pk'),
            content_type=ContentType.objects.get_for_model(instance)
        )

        if not hasattr(instance, reverse_relation):
            return None

        getattr(instance, reverse_relation).remove(generic_object)

        return Response(status=status.HTTP_204_NO_CONTENT)


class PhoneSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the Phone model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    number = PhoneNumberField(
        label=_('رقم الهاتف'),
        required=True
    )

    phone_type_display = serializers.CharField(
        source='get_phone_type_display',
        read_only=True
    )

    class Meta:
        model = admin_models.Phone
        fields = "__all__"
        read_only_fields = ('id', 'content_type', 'object_id', 'verified', 'primary', 'created_date', 'updated_date')

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
        instance = object_id.phones.create_generic_object(**validated_data)
        return instance


class PictureSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the Picture model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    picture_file = serializers.ImageField(
        required=True
    )

    class Meta:
        model = admin_models.Picture
        fields = "__all__"
        read_only_fields = ('id', 'content_type', 'object_id', 'created_date', 'updated_date')

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
        instance = object_id.pictures.create_generic_object(**validated_data)
        return instance


class FileSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the File model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    class Meta:
        model = admin_models.File
        fields = "__all__"
        read_only_fields = ('id', 'content_type', 'object_id', 'created_date', 'updated_date')
        extra_kwargs = {'file': {'required': True}}


class PhoneGenericRelationshipModelMixin(GenericRelationshipModelMixin):
    """
    This class is used to handle the phone number model
    """

    def add_phone(self, request, *args, **kwargs):
        """
        This function is used to add a new phone number to the model
        """

        return self.create_generic_object(request, PhoneSerializerMixin, _('تم إضافة رقم الهاتف بنجاح'))

    def delete_phone(self, pk, reverse_relation='phones', *args, **kwargs):
        """
        This function is used to add a new phone number to the model
        """

        return self.delete_generic_object(admin_models.Phone, pk, reverse_relation)


class PictureGenericRelationshipModelMixin(GenericRelationshipModelMixin):
    """
    This class is used to handle the picture model
    """

    def add_picture(self, request, *args, **kwargs):
        """
        This function is used to add a new phone number to the model
        """

        return self.create_generic_object(request, PictureSerializerMixin, _('تم إضافة الصورة بنجاح'))

    def delete_picture(self, pk, reverse_relation='pictures', *args, **kwargs):
        """
        This function is used to add a new phone number to the model
        """

        return self.delete_generic_object(admin_models.Picture, pk, reverse_relation)
