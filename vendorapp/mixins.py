import datetime

from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from utils import (
    constants, validators, serializers as utils_serializers, fields as utils_fields, mixins as utils_mixins
)

from adminapp import models as admin_model
from authapp import serializers as auth_serializers, mixins as auth_mixins
from vendorapp import models
from customerapp import models as customer_models
from . import shortcut, signals


class CurrentVendorDefault:
    """
    This class used to return customer object form http request
    """
    requires_context = True

    def __call__(self, serializer_field):
        """
        method enables Python programmers to write classes where the instances
        behave like functions and can be called like a function.
        :return: customer object
        """
        request = serializer_field.context.get('request', None)
        user = getattr(request, 'user', None)
        if hasattr(user, 'vendor_user'):
            return getattr(user.vendor_user, 'vendor')
        return None

    def __repr__(self):
        """
        special methods are a set of predefined methods used to enrich your classes.
        They start and end with double underscores.
        :return:
        """
        return '%s()' % self.__class__.__name__


class TagSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the tag model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    tag_type_display = serializers.CharField(
        source='get_tag_type_display',
        read_only=True
    )

    class Meta:
        abstract = True
        model = models.Tag
        fields = '__all__'
        read_only_fields = ('slug', 'is_active', 'activated_at', 'disabled_at', 'created_date', 'updated_date')


class VendorSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the vendor model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    city = serializers.SlugRelatedField(
        label=_('المدينة'),
        required=True,
        slug_field='slug',
        queryset=admin_model.City.activated.all()
    )

    tags = utils_fields.TagListSerializerField(
        label=_('الفئات'),
        slug_field='name',
        required=False,
        queryset=models.Tag.activated.all()
    )

    city_name = serializers.CharField(
        source='city.name',
        read_only=True
    )

    vendor_type_display = serializers.CharField(
        source='get_vendor_type_display',
        read_only=True
    )

    place_display = serializers.CharField(
        source='get_place_display',
        read_only=True
    )

    allowed_display = serializers.CharField(
        source='get_allowed_display',
        read_only=True
    )

    phones = utils_mixins.PhoneSerializerMixin(
        many=True,
        read_only=True
    )

    pictures = utils_mixins.PhoneSerializerMixin(
        many=True,
        read_only=True
    )

    status = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    def validate(self, attrs):
        """
        This function is used to verify the input before creating the object
        @param attrs: The inputs for create object
        @return: inputs
        """
        time_from = self.get_field_value('time_from')
        time_to = self.get_field_value('time_to')

        if time_from and not time_to or time_to and not time_from:
            raise serializers.ValidationError(
                detail=constants.Messages.TIME_FROM_AND_TO_ENTRY['message'],
                code=constants.Messages.TIME_FROM_AND_TO_ENTRY['code'],
            )

        return attrs

    class Meta:
        abstract = True
        model = models.Vendor
        fields = '__all__'
        read_only_fields = (
            'slug', 'vendor_type', 'parent', 'lft', 'rght', 'tree_id', 'level', 'payment_type', 'rate', 'is_active',
            'activated_at', 'disabled_at', 'is_deleted', 'deleted_at', 'created_date', 'updated_date'
        )

    def update(self, instance, validated_data):
        """
        Simply set each attribute on the instance, and then save it.
        Note that unlike `.create()` we don't need to treat many-to-many
        relationships as being a special case. During updates, we already
        have an instance pk for the relationships to be associated with.
        @param instance:
        @param validated_data:
        @return: Object of model
        """
        tags_data = validated_data.pop('tags', instance.tags.all())
        instance.tags.clear()
        instance.tags.add(*tags_data)
        return super(VendorSerializerMixin, self).update(instance, validated_data)


class BannerSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the banner model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendors = VendorSerializerMixin(
        many=True,
        read_only=True
    )

    banner_display = serializers.CharField(
        source='get_banner_type_display',
        read_only=True
    )

    class Meta:
        abstract = True
        model = models.Banner
        fields = '__all__'
        read_only_fields = ('is_active', 'activated_at', 'disabled_at', 'updated_date', 'created_date')


class PriceSerializerMixin(serializers.Serializer):
    """
    This class is used to display all price data such as price,
    tax and discount, as the system works in the Saudi currency and
    returns the data in an understandable way to customers
    """

    price_display = serializers.CharField(
        source='get_price_value_display',
        read_only=True
    )

    discount_display = serializers.CharField(
        source='get_discount_percent_display',
        read_only=True
    )

    discount_value = serializers.CharField(
        source='get_discount_value_display',
        read_only=True
    )

    tax_display = serializers.CharField(
        source='get_tax_percent_display',
        read_only=True
    )

    tax_value = serializers.CharField(
        source='get_tax_value_display',
        read_only=True
    )

    total_value_before_tax_value = serializers.CharField(
        source='get_total_value_before_tax',
        read_only=True
    )

    total_value_before_tax_display = serializers.CharField(
        source='get_total_value_before_tax_display',
        read_only=True
    )

    total = serializers.CharField(
        source='get_total_value',
        read_only=True
    )

    total_display = serializers.CharField(
        source='get_total_value_display',
        read_only=True
    )


class CommentSerializerMixin(serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the  comment model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    user = serializers.HiddenField(
        default=auth_mixins.CurrentUserDefault(),
        write_only=True
    )

    children = utils_fields.RecursiveField(
        many=True,
        read_only=True
    )

    user_name = serializers.CharField(
        source='user.get_full_name',
        read_only=True
    )

    user_username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    user_slug = serializers.CharField(
        source='user.slug',
        read_only=True
    )

    user_email = serializers.CharField(
        source='user.email',
        read_only=True
    )

    user_image_url = serializers.CharField(
        source='user.profile.get_image_url',
        read_only=True
    )

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(CommentSerializerMixin, self).__init__(*args, **kwargs)
        self.comment_object = self.context.get('comment_object', None)

    def validate(self, attrs):
        """
        This function is used to verify the input before creating the object
        @param attrs: The inputs for create object
        @return: inputs
        """
        if not hasattr(self.comment_object, 'comment'):
            raise serializers.ValidationError(
                detail=constants.Messages.COMMENT_OBJECT_ERROR['message'],
                code=constants.Messages.COMMENT_OBJECT_ERROR['code'],
            )

        return attrs

    class Meta:
        model = models.Comment
        exclude = ('lft', 'rght', 'tree_id', 'level', 'content_type', 'object_id')
        read_only_fields = ('prent', 'is_active', 'activated_at', 'disabled_at', 'created_date', 'updated_date')

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        return self.comment_object.comment.create(**validated_data)


class ServiceSerializerMixin(PriceSerializerMixin, utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the service model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendor = serializers.HiddenField(
        default=CurrentVendorDefault(),
        write_only=True
    )

    tags = utils_fields.TagListSerializerField(
        label=_('الفئات'),
        slug_field='name',
        required=False,
        queryset=models.Tag.activated.all()
    )

    image_file = serializers.ImageField(
        required=False
    )

    image = serializers.URLField(
        source='get_image_url',
        read_only=True
    )

    type_display = serializers.CharField(
        source='get_type_display',
        read_only=True
    )

    place_display = serializers.CharField(
        source='get_place_display',
        read_only=True
    )

    schedule_display = serializers.CharField(
        source='get_schedule_display',
        read_only=True
    )

    time_display = serializers.CharField(
        source='get_time_display',
        read_only=True
    )

    comment = CommentSerializerMixin(
        source='get_comment_objects',
        many=True,
        read_only=True
    )

    def validate_name(self, name):
        """
        This function is used to verify the input before creating the object
        @param name: The name of service
        @return: name
        """
        vendor = self.fields['vendor'].default(self)
        return name

    class Meta:
        model = models.Service
        exclude = ('is_active', 'activated_at', 'disabled_at', 'is_deleted', 'deleted_at')
        read_only_fields = ('slug', 'type', 'created_date', 'updated_date')
        validators = [
            validators.RequiredTogetherValidator(
                fields=["hour", "minute"]
            )
        ]

    def update(self, instance, validated_data):
        """
        Simply set each attribute on the instance, and then save it.
        Note that unlike `.create()` we don't need to treat many-to-many
        relationships as being a special case. During updates we already
        have an instance pk for the relationships to be associated with.
        @param instance:
        @param validated_data:
        @return: Object of model
        """
        tags_data = validated_data.pop('tags', instance.tags.all())
        instance.tags.clear()
        instance.tags.add(*tags_data)
        return super(ServiceSerializerMixin, self).update(instance, validated_data)

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """

        tags_data = validated_data.pop('tags', [])
        vendor = validated_data.pop('vendor')
        instance = self.Meta.model.sales_objects.create(**validated_data, type=vendor.vendor_type)
        instance.sales.create(vendor=vendor)
        instance.tags.add(*tags_data)
        return instance


class EmployeeSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the employee model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendor = serializers.HiddenField(
        default=CurrentVendorDefault(),
        write_only=True
    )

    image_file = serializers.ImageField(
        required=False,
        write_only=True
    )

    image = serializers.URLField(
        source='get_image_url',
        read_only=True
    )

    class Meta:
        abstract = True
        model = models.Employee
        exclude = ('service',)
        read_only_fields = ("created_date", "updated_date")


class AvailabilitySerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the availability model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendor = serializers.HiddenField(
        default=CurrentVendorDefault(),
        write_only=True
    )

    days = serializers.IntegerField(
        label=_('عدد أيام التكرار'),
        min_value=1,
        max_value=90,
        required=False,
        write_only=True
    )

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(AvailabilitySerializerMixin, self).__init__(*args, **kwargs)
        vendor = self.fields.pop('vendor').get_default()
        schedules = models.Service.ScheduleTypeChoices
        if vendor is not None:
            self.fields['service'] = serializers.PrimaryKeyRelatedField(
                label=_('الخدمة'),
                queryset=models.Service.sales_objects.all_sales(vendor=vendor, schedule=schedules.DEFAULT)
            )

            self.fields['employee'] = serializers.PrimaryKeyRelatedField(
                label=_('الموظفين'),
                required=False,
                queryset=models.Employee.verified_objects.all_employees(vendor=vendor)
            )

    def get_time_delta(self, time):
        """
        this function used to return time delta
        @return: time delta
        """
        return shortcut.time2delta(time)

    def validate_total(self, service, start, end):
        """
        this function used to validate total value
        @return: total
        """

        total = self.get_time_delta(service)

        if (end - start) < total:
            raise serializers.ValidationError(
                detail=constants.Messages.TOTAL_TIME_EQUAL_OR_LESS_THAN_SERVICE_TOTAL_TIME['message'],
                code=constants.Messages.TOTAL_TIME_EQUAL_OR_LESS_THAN_SERVICE_TOTAL_TIME['code']
            )

        return total

    def validate_date(self, date):
        """
        This function is used to verify the input before creating the object
        @return: date
        """
        current_date = shortcut.current_datetime().date()
        if date < current_date:
            raise serializers.ValidationError(
                detail=constants.Messages.DATE_LESS_THAN_CURRENT_DATE['message'],
                code=constants.Messages.DATE_LESS_THAN_CURRENT_DATE['code']
            )
        return date

    def validate(self, attrs):
        """
        This function is used to verify the input before creating the object
        @param attrs: The inputs for create object
        @return: inputs
        """

        service = attrs['service']
        employee = attrs.get('employee', None)
        date = attrs.pop('date')
        days = attrs.pop('days', 1)

        start = self.get_time_delta(attrs['start'])
        end = self.get_time_delta(attrs['end'])

        self.validate_total(service, start, end)
        attrs['date_lys'] = self.get_date_list(service, employee, date, days, start, end)
        return attrs

    def get_queryset(self, **kwargs):
        """
        is determined what is queryset must be found
        @return: queryset
        """

        date_lys = kwargs['date_lys']
        service = kwargs['service']
        employee = kwargs.get('employee', None)
        manager = self.Meta.model.objects

        if employee is not None:
            query = Q(employee=employee, date__in=date_lys)
        else:
            query = Q(service=service, employee__isnull=True, date__in=date_lys)

        return self.Meta.model.objects.filter(query)

    def get_date_list(self, service, employee, date, days, start, end):
        """
        this function used to get all date form days and return it.
        @return: list of date
        """

        date_lys = [date + datetime.timedelta(days=day) for day in range(days)]
        date_lys = dict(zip(date_lys, date_lys))
        query = self.get_queryset(date_lys=date_lys, service=service, employee=employee)

        for row in query:
            if start >= row.to_time or end <= row.from_time:
                pass
            else:
                date_lys.pop(row.date)

        return date_lys

    class Meta:
        abstract = True
        model = models.Availability
        fields = '__all__'
        read_only_fields = ('created_date', 'updated_date')

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        date_lys = validated_data.pop('date_lys')
        instances = [self.Meta.model.objects.create(date=date, **validated_data) for date in date_lys]
        return instances


class BankAccountSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the bank model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendor = serializers.HiddenField(
        default=CurrentVendorDefault(),
        write_only=True
    )

    class Meta:
        abstract = True
        model = models.BankAccount
        fields = '__all__'
        read_only_fields = ("created_date", "updated_date")


class WithdrawRequestSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the withdrawal request model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendor = serializers.HiddenField(
        default=CurrentVendorDefault(),
        write_only=True
    )

    invoices = utils_mixins.FileSerializerMixin(
        many=True
    )

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(WithdrawRequestSerializerMixin, self).__init__(*args, **kwargs)
        vendor = self.get_field_value('vendor')

        if not vendor:
            return

        self.fields['bank'] = serializers.PrimaryKeyRelatedField(
            label=_('الحساب البنكي'),
            queryset=models.BankAccount.objects.all_banks(vendor=vendor)
        )

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        self.fields['bank'] = BankAccountSerializerMixin()
        self.fields['amount_display'] = serializers.CharField(source='get_amount_display')
        self.fields['status_display'] = serializers.CharField(source='get_status_display')
        return super(WithdrawRequestSerializerMixin, self).to_representation(instance)

    class Meta:
        abstract = True
        model = models.WithdrawRequest
        fields = '__all__'
        read_only_fields = ('status', 'notes', 'created_date', 'updated_date')

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        invoices = validated_data.pop('invoices')
        instance = super(WithdrawRequestSerializerMixin, self).create(validated_data)
        [instance.invoices.create(**invoice) for invoice in invoices]
        signals.create_withdraw_request.send(
            sender=instance.__class__, user=self.context['request'].user,
            amount=instance.get_amount_display
        )
        return instance


class OfferSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the offer request model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendor = serializers.HiddenField(
        default=CurrentVendorDefault(),
        write_only=True
    )

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        self.fields['users_count'] = serializers.CharField(source='get_users_count')
        return super(OfferSerializerMixin, self).to_representation(instance)

    def validate_expire_date(self, expire_date):
        """
        This function is used to verify the input before creating the object
        @return: date
        """
        current_date = shortcut.current_datetime().date()
        if expire_date < current_date:
            raise serializers.ValidationError(
                detail=constants.Messages.DATE_LESS_THAN_CURRENT_DATE['message'],
                code=constants.Messages.DATE_LESS_THAN_CURRENT_DATE['code']
            )

        return expire_date

    def validate_code(self, code):
        """
        This function is used to verify the input before creating the object
        @return: date
        """
        if self.Meta.model.offer_objects.actives(code=code).exists():
            raise serializers.ValidationError(
                detail=constants.Messages.CODE_ALREADY_EXISTS['message'],
                code=constants.Messages.CODE_ALREADY_EXISTS['code']
            )
        return code

    class Meta:
        abstract = True
        model = models.Offer
        fields = '__all__'
        read_only_fields = (
            'type', 'users', 'is_active', 'activated_at', 'disabled_at', 'is_deleted', 'deleted_at', 'created_date',
            'updated_date'
        )

    def create(self, validated_data):
        """
        this function  is used to create offer code
        @param validated_data: the data we pass to offer
        @return: object
        """
        return self.Meta.model.offer_objects.create_offer_vendor(**validated_data)


class OrderItemSerializerMixin(PriceSerializerMixin, utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the order item model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    service = ServiceSerializerMixin(
        source='sales.services.first',
        read_only=True
    )

    employee = EmployeeSerializerMixin(
        read_only=True
    )

    address = auth_mixins.AddressSerializerMixin(
        read_only=True
    )

    class Meta:
        model = customer_models.OrderItem
        exclude = ('order',)
        read_only_fields = ('id', 'created_date', 'updated_date')


class OrderSerializerMixin(PriceSerializerMixin, utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the order model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    customer = auth_serializers.UserSerializer(
        source='customer.user',
        read_only=True
    )

    order_item = OrderItemSerializerMixin(
        many=True,
        read_only=True
    )

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        abstract = True
        model = customer_models.Order
        fields = '__all__'
        read_only_fields = ('id', 'vendor', 'customer', 'is_deleted', 'deleted_at', 'created_date', 'updated_date')
