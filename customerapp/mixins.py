import datetime

from django.conf import settings
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from authapp import serializers as auth_serializer, mixins as auth_mixins, models as auth_models
from utils import constants, validators, serializers as utils_serializers
from vendorapp import mixins as vendor_mixins, models as vendor_models, shortcut as vendor_shortcut
from . import models, signals, alrajhi, shortcut, tamara


class RequiredFieldsMixins:
    """
    This class is used to add the required fields by passing
    them to the variable required_fields
    """

    required_fields = []

    def get_queryset(self):
        """
        this function used to return queryset to this class
        @return: queryset
        """
        for field in self.required_fields:
            if field not in self.request.query_params.keys():
                return self.queryset.none()

        return super(RequiredFieldsMixins, self).get_queryset()


class CurrentCustomerDefault:
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
        return getattr(user, 'customer', None)

    def __repr__(self):
        """
        special methods are a set of predefined methods used to enrich your classes.
        They start and end with double underscores.
        :return:
        """
        return '%s()' % self.__class__.__name__


class TagSerializerMixin(vendor_mixins.TagSerializerMixin):
    """
    This class can handle the add and modify functions of the tag model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class VendorSerializerMixin(vendor_mixins.VendorSerializerMixin):
    """
    This class can handle the add and modify functions of the vendor model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    user = auth_serializer.UserSerializer(
        source='get_users',
        many=True,
        read_only=True
    )


class BannerSerializerMixin(vendor_mixins.BannerSerializerMixin):
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


class CommentSerializerMixin(vendor_mixins.CommentSerializerMixin):
    """
    This class can handle the add and modify functions of the  comment model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class ServiceSerializerMixin(vendor_mixins.ServiceSerializerMixin):
    """
    This class can handle the add and modify functions of the service model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class EmployeeSerializerMixin(vendor_mixins.EmployeeSerializerMixin):
    """
    This class can handle the add and modify functions of the employee model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class AvailabilitySerializerMixin(vendor_mixins.AvailabilitySerializerMixin):
    """
    This class can handle the add and modify functions of the availability model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class WalletSerializerMixin(auth_mixins.WalletSerializerMixin):
    """
    This class can handle the add and modify functions of the wallet model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class OrderItemSerializerMixin(vendor_mixins.OrderItemSerializerMixin):
    """
    This class can handle the add and modify functions of the order item model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class OrderSerializerMixin(vendor_mixins.OrderSerializerMixin):
    """
    This class can handle the add and modify functions of the order model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    customer = serializers.HiddenField(
        default=CurrentCustomerDefault(),
        write_only=True
    )

    vendor = VendorSerializerMixin(
        read_only=True
    )

    order_item = OrderItemSerializerMixin(
        many=True,
        read_only=True
    )

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """

        super(OrderSerializerMixin, self).__init__(*args, **kwargs)
        customer = self.get_field_value('customer')
        self.fields['address'] = serializers.PrimaryKeyRelatedField(
            label=_('العنوان'),
            required=False,
            queryset=auth_models.Address.activated.filter(user=customer.user),
        )

    def validate_addresses(self, service, address):
        """
        this function is used to validate address using service mode
        @return: address
        """
        home = vendor_models.Service.PlaceChoices.HOME
        if service.place == home and not address:
            raise serializers.ValidationError(
                detail=constants.Messages.ADDRESS_REQUIRED_ERROR['message'],
                code=constants.Messages.ADDRESS_REQUIRED_ERROR['code'],
            )
        return address

    def create_order_item(self, order, **kwargs):
        """
        this function used to create order item by order
        @param order:
        @param kwargs:
        @return:
        """
        return order.order_item.create(**kwargs)

    def create_order(self, service, **kwargs):
        """
        this function used to create order by service
        @param service: the service object
        @return: order
        """
        customer = kwargs.pop('customer')
        vendor = service.get_vendor()
        sales = service.sales.first()
        price = service.price
        discount = service.discount
        tax = service.tax
        payment_type = vendor.payment_type

        order = self.Meta.model.verified_objects.create(customer=customer, vendor=vendor, payment_type=payment_type)
        order_item = self.create_order_item(order=order, sales=sales, price=price, discount=discount, tax=tax, **kwargs)
        signals.order_create.send(
            sender=order.__class__, order=order, customer=customer, vendor=vendor,
            service=service
        )
        return order


class CreateOrderScheduleSerializerMixin(OrderSerializerMixin):
    """
    This class is used to add an order of a scheduled type where
    the availability number is entered with the start time and end time
    """

    availability = serializers.PrimaryKeyRelatedField(
        label=_('رقم ألإتاحة'),
        queryset=vendor_models.Availability.objects.activated_availabilities(),
        write_only=True
    )

    start = serializers.TimeField(
        label=_('بداية الحجز'),
        write_only=True
    )

    end = serializers.TimeField(
        label=_('نهاية الحجز'),
        write_only=True
    )

    def validate_range(self, availability, start, end):
        """
        this function is used to validate range time
        @return: availability
        """
        range_time = vendor_shortcut.get_range_date_list(availability)
        if [start, end] not in range_time:
            raise serializers.ValidationError(
                detail=constants.Messages.ORDER_AVAILABILITY_UNIQUE_ERROR['message'],
                code=constants.Messages.ORDER_AVAILABILITY_UNIQUE_ERROR['code'],
            )
        return start, end

    def validate(self, attrs):
        """
        this function is used to validate all data
        @param attrs: all data
        @return: all data
        """

        availability = attrs.get('availability')
        service = availability.service

        address = attrs.get('address', None)
        start = attrs.get('start')
        end = attrs.get('end')

        self.validate_range(availability, start, end)
        self.validate_addresses(service, address)

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
        availability = validated_data['availability']
        service = availability.service
        employee = getattr(availability, 'employee', None)
        date = availability.date
        return self.create_order(service, employee=employee, date=date, **validated_data)


class CreateOrderUnscheduleSerializerMixin(OrderSerializerMixin):
    """
    This class is used to add an order of an unscheduled type where
    the service is passed directly without adding availability
    """

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(CreateOrderUnscheduleSerializerMixin, self).__init__(*args, **kwargs)
        unschedule = vendor_models.Service.ScheduleTypeChoices.UNSCHEDULED
        self.fields['service'] = serializers.PrimaryKeyRelatedField(
            label=_('الخدمة'),
            queryset=vendor_models.Service.sales_objects.filter(schedule=unschedule),
            write_only=True
        )

    def validate(self, attrs):
        """
        this function is used to validate all data
        @param attrs: all data
        @return: all data
        """

        service = attrs.get('service', None)
        address = attrs.get('address', None)
        self.validate_addresses(service, address)

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
        service = validated_data.pop('service')
        return self.create_order(service=service, **validated_data)


class PaymentSerializerMixin(utils_serializers.Serializer):
    """
    This class can handle the add and modify functions of the payment model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """
    PAYMENT_TYPE_DEFAULT = models.Order.PaymentTypeChoices.SYSTEM

    customer = serializers.HiddenField(
        default=CurrentCustomerDefault(),
        write_only=True
    )

    offer_code = serializers.CharField(
        label=_('كود الخصم'),
        max_length=150,
        validators=[
            RegexValidator(
                regex=validators.alphanumeric,
                message=constants.Messages.OFFER_FORMAT_ERROR['message']
            ),
            MinLengthValidator(4),
            MaxLengthValidator(12)
        ],
        write_only=True,
        required=False
    )

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(PaymentSerializerMixin, self).__init__(*args, **kwargs)
        self.customer = self.fields.pop('customer').get_default()
        self.order = None
        self.offer = None
        self.total = None
        self.fields['order'] = serializers.PrimaryKeyRelatedField(
            label=_('الطلب'),
            queryset=models.Order.verified_objects.approval(
                customer=self.customer, payment_type=self.PAYMENT_TYPE_DEFAULT
            )
        )

    def get_offer_object(self, code):
        """
        this function is used to validate offer code
        @return: offer code
        """

        offer_code = vendor_models.Offer.verified_objects.verified(
            code=code, vendor=self.order.vendor,
            user=self.customer.user
        )

        if code and not offer_code:
            raise serializers.ValidationError(
                detail=constants.Messages.OFFER_EXPIRE_ERROR['message'],
                code=constants.Messages.OFFER_EXPIRE_ERROR['code'],
            )

        return offer_code

    def validate(self, attrs):
        """
        this function is used to validate all data
        @param attrs: all data
        @return: all data
        """

        code = attrs.pop('offer_code', None)
        self.order = attrs.pop('order')
        self.offer = self.get_offer_object(code)
        self.total = self.get_total_value()
        return attrs

    def get_discount_percent(self):
        """
        this function used to calculate discount percent
        @return: discount percent
        """

        return getattr(self.offer, 'discount', 0)

    def get_discount_value(self):
        """
        this function used to calculate discount value
        @return: discount value
        """
        discount = vendor_shortcut.get_discount_value(self.order.price, self.get_discount_percent())
        return shortcut.get_correct_discount_value(discount)

    def get_total_value_before_tax(self):
        """
        this function used to calculate total value before tax value
        @return: total value before tax value
        """

        return vendor_shortcut.get_total_value_before_tax(self.order.price, self.get_discount_value())

    def get_tax_percent(self):
        """
        this function used to calculate tax percent
        @return: tax percent
        """

        return getattr(self.order, 'tax', 0)

    def get_tax_value(self):
        """
        this function used to calculate tax value
        @return: tax value
        """

        return vendor_shortcut.get_tax_value(self.get_total_value_before_tax(), self.get_tax_percent())

    def get_total_value(self):
        """
        this function used to calculate total value
        @return: total
        """
        assert self.order is not None, (
            "'%s' should either include a `order` attribute"
        )

        return vendor_shortcut.get_total_value(self.get_total_value_before_tax(), self.get_tax_value())

    def get_price_display(self, price):
        """
        This function is used to convert price value to price display
        @return: price display
        """
        return vendor_shortcut.get_intcomma_display(price)

    def get_dict_object(self):
        """
        this function used to convert all data members to dict
        @return: dict
        """
        return dict(
            discount_percent="{}%".format(self.get_discount_percent()),
            discount_value=self.get_price_display(self.get_discount_value()),
            total_value_before_tax=self.get_price_display(self.get_total_value_before_tax()),
            tax_percent="{}%".format(self.get_tax_percent()),
            tax_value=self.get_price_display(self.get_tax_value()),
            total_value=self.get_price_display(self.get_total_value())
        )


class OfferCodeSerializerMixin(PaymentSerializerMixin):
    """
    This class is used to verify the discount code by passing the code with
    the owner of this discount
    """

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(OfferCodeSerializerMixin, self).__init__(*args, **kwargs)
        self.fields['offer_code'].required = True

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """

        return self.get_dict_object()


class AlrajhiGetPageURLSerializerMixin(PaymentSerializerMixin, utils_serializers.ModelSerializer):
    """
    This class is used through payment via Al-Rajhi,
    as it returns the Al-Rajhi page with the appropriate amount for
    the payment process
    """

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(AlrajhiGetPageURLSerializerMixin, self).__init__(*args, **kwargs)
        self.request = self.context['request']
        self.page = None

    def get_page_url(self):
        """
        this function used to get page url from page
        @return: url
        """
        return self.page['url'].split(":", 1)

    def get_total_value(self):
        """
        this function used to calculate total value
        @return: total
        """
        pay_via_wallet = self.get_field_value('pay_via_wallet')
        amount = super(AlrajhiGetPageURLSerializerMixin, self).get_total_value()
        wallet = self.customer.wallet

        if not pay_via_wallet:
            return amount

        if wallet.is_withdraw_valid(amount):
            raise serializers.ValidationError(
                detail=constants.Messages.PAY_VIA_WALLET_ERROR['message'],
                code=constants.Messages.PAY_VIA_WALLET_ERROR['code']
            )

        return amount - wallet.balance

    def validate(self, attrs):
        """
        this function is used to validate all data
        @param attrs: all data
        @return: all data
        """
        attrs = super(AlrajhiGetPageURLSerializerMixin, self).validate(attrs)
        self.page = alrajhi.Alrajhi(self.request).get_page(self.total)

        if self.page is None:
            raise serializers.ValidationError(
                detail=constants.Messages.GET_PAYMENT_PAGE_ERROR['message'],
                code=constants.Messages.GET_PAYMENT_PAGE_ERROR['code']
            )

        return attrs

    class Meta:
        abstract = True
        model = models.AlRajhiPaymentPageURL
        fields = ('customer', 'offer_code', 'pay_via_wallet',)

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        url = self.get_page_url()
        return self.Meta.model.objects.create(
            order=self.order, offer=self.offer, customer=self.customer,
            page_id=url[0], page_url=url[1], track_id=self.page['track'], amount=self.total,
            **validated_data
        )


class WalletPaymentSerializerMixin(PaymentSerializerMixin):
    """
    This class is used in the payment process through the wallet,
    where the value of the paid amount is verified.
    If the wallet does not have enough amount, an error is returned
    """

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(WalletPaymentSerializerMixin, self).__init__(*args, **kwargs)
        self.wallet = self.customer.wallet

    def validate(self, attrs):
        """
        this function is used to validate all data
        @param attrs: all data
        @return: all data
        """
        attrs = super(WalletPaymentSerializerMixin, self).validate(attrs)
        if not self.wallet.is_withdraw_valid(self.total):
            raise serializers.ValidationError(
                detail=constants.Messages.ORDER_PAY_BALANCE_LESS_THAN_PRICE_ERROR['message'],
                code=constants.Messages.ORDER_PAY_BALANCE_LESS_THAN_PRICE_ERROR['code'],
            )

        self.wallet.withdraw(self.total, self.customer.user)
        return attrs

    def create_invoice_object(self):
        """
        This function is used to generate the invoice
        @return: invoice object
        """
        return models.Invoice.verified_objects.create_invoice(self.order, self.offer)

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """

        invoice = self.create_invoice_object()
        payment = models.WalletProvider.objects.create_payment(invoice, wallet=self.wallet, amount=self.total)
        signals.wallet_payment_success.send(sender=self.order.__class__, order=self.order, invoice=invoice)
        return self.wallet


class AlrajhiPaymentSerializerMixin(utils_serializers.Serializer):
    """
    This class is used to confirm the payment process through Al-Rajhi,
    as the data is returned through the Al-Rajhi gateway
    """

    REQUIRED_FIELDS = ['paymentid', 'tranid', 'trackid', 'amt', 'result', 'ref']

    trandata = serializers.CharField(
        label=_('البيانات المشفرة'),
    )

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(AlrajhiPaymentSerializerMixin, self).__init__(*args, **kwargs)
        self.page = None
        self.response = None

    def get_expire_date(self):
        """
        This function is used to get expire_date
        @return: expire_date
        """
        return vendor_shortcut.current_datetime() - datetime.timedelta(minutes=settings.PAYMENT_GATEWAY_TIME_FACTOR)

    def get_page_object(self, trandata):
        """
        This function is used to validate required fields for check trandata
        @param trandata: Cipher text via Al Rajhi Gate
        @return:page
        """

        response = alrajhi.Alrajhi(self.context['request']).get_data(trandata)

        for field in self.REQUIRED_FIELDS:
            if field not in response.keys():
                raise ValueError()

        page = models.AlRajhiPaymentPageURL.activated.get(
            page_id=response.get('paymentid'),
            track_id=response.get('trackid'),
            created_date__gte=self.get_expire_date()
        )

        if bool(not page.order.is_approval or response.get('result') != 'CAPTURED'):
            raise ValueError()

        response['trandata'] = trandata
        response['amt'] = float(response['amt']) if isinstance(response['amt'], str) else response['amt']

        if int(page.amount) > int(response['amt']):
            raise ValueError()

        return page, response

    def validate(self, attrs):
        """
        this function is used to validate all data
        @param attrs: all data
        @return: all data
        """

        trandata = attrs['trandata']
        self.page, self.response = self.get_page_object(trandata)
        return attrs

    def create_invoice_object(self):
        """
        This function is used to generate the invoice
        @return: invoice object
        """
        return models.Invoice.verified_objects.create_invoice(self.page.order, self.page.offer)

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        invoice = self.create_invoice_object()
        wallet = self.page.customer.wallet

        if self.page.pay_via_wallet:
            payment = models.AlRajhiWithWalletProvider.objects.create_payment(wallet=wallet, invoice=invoice,
                                                                              **self.response)
        else:
            payment = models.AlRajhiProvider.objects.create_payment(invoice=invoice, **self.response)

        signals.alrajhi_payment_success.send(sender=self.page.order.__class__, order=self.page.order, invoice=invoice)
        return self.page


class TamaraGetPageURLSerializerMixin(PaymentSerializerMixin, utils_serializers.ModelSerializer):
    """
    This class is used to confirm the payment process through Tamara,
    as the data is returned through the Tamara gateway
    """

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(TamaraGetPageURLSerializerMixin, self).__init__(*args, **kwargs)
        self.request = self.context['request']
        self.response = None

    def get_page_url(self):
        """
        this function used to get page url from page
        @return: url
        """
        return self.response['checkout_url']

    def validate(self, attrs):
        """
        this function is used to validate all data
        @param attrs: all data
        @return: all data
        """

        attrs = super(TamaraGetPageURLSerializerMixin, self).validate(attrs)
        try:
            self.response = tamara.Tamara(self.request).create_checkout_session(
                order=self.order,
                total=self.total,
                tax=self.get_tax_value(),
                discount=self.get_discount_value()
            )
        except (Exception,):
            raise serializers.ValidationError(
                detail=constants.Messages.GET_PAYMENT_PAGE_ERROR['message'],
                code=constants.Messages.GET_PAYMENT_PAGE_ERROR['code']
            )
        return attrs

    class Meta:
        abstract = True
        model = models.TamaraPaymentPageURL
        fields = ('customer', 'offer_code',)

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """

        return self.Meta.model.objects.create(
            order=self.order,
            offer=self.offer,
            customer=self.customer,
            amount=self.total,
            order_track_id=self.response['order_id'],
            checkout_id=self.response['checkout_id'],
            checkout_url=self.get_page_url(),
        )


class TamaraPaymentSerializerMixin(utils_serializers.Serializer):
    """
    This class is used to confirm the payment process through Tamara,
    as the data is returned through the Tamara gateway
    """

    order_id = serializers.CharField(
        label=_('رقم الطلب'),
    )

    order_reference_id = serializers.CharField(
        label=_('رقم مرجع الطلب'),
    )

    order_status = serializers.CharField(
        label=_('رقم مرجع الطلب'),
    )

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(TamaraPaymentSerializerMixin, self).__init__(*args, **kwargs)
        self.request = self.context['request']
        self.page = None
        self.response = None

    def get_page_object(self, attrs):
        """
        This function is used to validate required fields for check trandata
        @param attrs: all data
        @return:page
        """
        client = tamara.Tamara(self.request)
        order_track_id = attrs['order_id']
        order_status = attrs['order_status']
        page = models.TamaraPaymentPageURL.objects.get(order_track_id=order_track_id)

        if bool(not page.order.is_approval or order_status != 'approved'):
            raise ValueError()

        response = client.authorise(order_track_id)

        if response['status'] != 'authorised':
            raise ValueError()

        response = client.capture(order_track_id, page.amount)

        if not response.get('capture_id', None):
            raise ValueError()

        return page, response

    def validate(self, attrs):
        """
        this function is used to validate all data
        @param attrs: all data
        @return: all data
        """

        self.page, self.response = self.get_page_object(attrs)
        self.response.update({'amt': self.page.amount})
        return attrs

    def create_invoice_object(self):
        """
        This function is used to generate the invoice
        @return: invoice object
        """
        return models.Invoice.verified_objects.create_invoice(self.page.order, self.page.offer)

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        invoice = self.create_invoice_object()
        payment = models.TamaraProvider.objects.create_payment(invoice=invoice, **self.response)
        signals.tamara_payment_success.send(sender=self.page.order.__class__, order=self.page.order, invoice=invoice)
        return self.page
