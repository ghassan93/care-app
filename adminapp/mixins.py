from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.serializer_fields import CountryField

from rest_framework import serializers

from utils import constants, serializers as utils_serializers

from authapp import mixins as auth_mixins, tokens, tasks
from vendorapp import mixins as vendor_mixins, models as vendor_models
from customerapp import models as customer_models, mixins as customer_mixins
from . import forms, signals, models

USER_MODEL = get_user_model()


class PasswordChangeSerializerMixin(auth_mixins.PasswordChangeSerializerMixin):
    """
    This class is used to modify a user's password.
    Where the new password is entered with confirm password
    """

    oldpassword = None
    form_class = forms.ChangePasswordForm


class UserSerializerMixin(auth_mixins.UserSerializerMixin):
    """
    This class can handle the add and modify functions of the user model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    absolute_url = serializers.SerializerMethodField(
        source='get_absolute_url',
        read_only=True
    )

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('admin:api:user-detail', kwargs={'slug': obj.slug})


class VendorSerializerMixin(vendor_mixins.VendorSerializerMixin):
    """
    This class can handle the add and modify functions of the vendor model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    absolute_url = serializers.SerializerMethodField(
        source='get_absolute_url',
        read_only=True
    )

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('admin:api:vendor-detail', kwargs={'slug': obj.slug})


class CommentSerializerMixin(vendor_mixins.CommentSerializerMixin):
    """
    This class can handle the add and modify functions of the  comment model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendor_name = serializers.CharField(
        source='comment_object.get_vendor',
        read_only=True
    )

    service_name = serializers.CharField(
        source='comment_object.name',
        read_only=True
    )

    absolute_url = serializers.SerializerMethodField(
        source='get_absolute_url',
        read_only=True
    )

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('admin:api:comment-detail', kwargs={'pk': obj.pk})


class ServiceSerializerMixin(vendor_mixins.ServiceSerializerMixin):
    """
    This class can handle the add and modify functions of the service model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendor_name = serializers.CharField(
        source='get_vendor.name',
        read_only=True
    )

    absolute_url = serializers.SerializerMethodField(
        source='get_absolute_url',
        read_only=True
    )

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('admin:api:service-detail', kwargs={'slug': obj.slug})


class WithdrawRequestSerializerMixin(vendor_mixins.WithdrawRequestSerializerMixin):
    """
    This class can handle the add and modify functions of the withdrawal request model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendor = None

    vendor_name = serializers.CharField(
        source='vendor.name',
        read_only=True
    )

    absolute_url = serializers.SerializerMethodField(
        source='get_absolute_url',
        read_only=True
    )

    class Meta(vendor_mixins.WithdrawRequestSerializerMixin.Meta):
        read_only_fields = ('vendor', 'amount', 'created_date', 'updated_date')

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('admin:api:withdraw-request-detail', kwargs={'pk': obj.pk})


class OfferSerializerMixin(vendor_mixins.OfferSerializerMixin):
    """
    This class can handle the add and modify functions of the offer request model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendor = VendorSerializerMixin(
        label=_('البائعين'),
        required=False,
        read_only=True
    )

    absolute_url = serializers.SerializerMethodField(
        source='get_absolute_url',
        read_only=True
    )

    def create(self, validated_data):
        """
        this function  is used to create offer code
        @param validated_data: the data we pass to offer
        @return: object
        """
        request = self.context['request']
        code = self.Meta.model.offer_objects.create_offer_admin(**validated_data)
        signals.create_offer_code.send(sender=code.__class__, request=request, user=request.user)
        return code

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('admin:api:offer-detail', kwargs={'pk': obj.pk})


class ActiveOfferSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class is used to activate discount codes that have been added
    via the control panel.
    Where a discount code is sent to all developer accounts within the system,
    and through this code, he can activate the discount code that was created
    """

    otp = serializers.CharField(
        label=_("رمز التحقق"),
        required=True,
        max_length=settings.ACCOUNT_CODE_MAX_LENGTH,
        min_length=settings.ACCOUNT_CODE_MIN_LENGTH
    )

    def validate_otp(self, otp):
        """
        validate otp is unique in same time by check is active or not
        @param otp: the one time password
        @return: otp
        """
        if not tokens.password_reset_token_generator.check_token(settings.SECRET_KEY, otp):
            raise serializers.ValidationError(
                detail=constants.Messages.INVALID_CODE['message'],
                code=constants.Messages.INVALID_CODE['code']
            )
        return otp

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
        instance.is_active = True
        instance.save()
        return instance


class CitySerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the city model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    country = CountryField(
        label=_('الدولة'),
        required=True
    )

    absolute_url = serializers.SerializerMethodField(
        source='get_absolute_url',
        read_only=True
    )

    class Meta:
        model = models.City
        fields = '__all__'
        read_only_fields = ('slug', 'is_active', 'activated_at', 'disabled_at', 'created_date', 'updated_date')

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('admin:api:city-detail', kwargs={'slug': obj.slug})


class PoliciesSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the policies model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    content = serializers.CharField(
        label=_('المحتوى'),
        required=True,
        write_only=True
    )

    content_en = serializers.CharField(
        label=_('المحتوى باللغة الانجليزية'),
        required=False,
        write_only=True
    )

    absolute_url = serializers.SerializerMethodField(
        source='get_absolute_url',
        read_only=True
    )

    class Meta:
        model = models.Policies
        fields = 'all'
        read_only_fields = ('id', 'slug', 'is_active', 'created_date', 'updated_date')

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('admin:api:policies-detail', kwargs={'slug': obj.slug})


class TagSerializerMixin(vendor_mixins.TagSerializerMixin):
    """
    This class can handle the add and modify functions of the tag model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    absolute_url = serializers.SerializerMethodField(
        source='get_absolute_url',
        read_only=True
    )

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('admin:api:tag-detail', kwargs={'slug': obj.slug})


class BannerSerializerMixin(vendor_mixins.BannerSerializerMixin):
    """
    This class can handle the add and modify functions of the banner model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendors = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        queryset=vendor_models.Vendor.verified_objects.all()
    )

    banner_type_display = serializers.CharField(
        source='get_banner_type_display',
        read_only=True
    )

    absolute_url = serializers.SerializerMethodField(
        source='get_absolute_url',
        read_only=True
    )

    def __init__(self, *args, **kwargs):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        super(BannerSerializerMixin, self).__init__(*args, **kwargs)

        if not self.is_put_action():
            return

        initial_data = getattr(self, 'initial_data', None)
        image = initial_data.get('image', None)
        if not image:
            self.fields.pop('image')

    def create(self, validated_data):
        """
        this function  is used to create offer code
        @param validated_data: the data we pass to offer
        @return: object
        """
        vendors = validated_data.pop('vendors', [])
        banner = super(BannerSerializerMixin, self).create(validated_data)
        banner.vendors.add(*vendors)
        return banner

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('admin:api:banner-detail', kwargs={'pk': obj.pk})


class OrderSerializerMixin(vendor_mixins.OrderSerializerMixin):
    """
    This class can handle the add and modify functions of the order model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    vendor = VendorSerializerMixin(
        read_only=True
    )

    absolute_url = serializers.SerializerMethodField(
        source='get_absolute_url',
        read_only=True
    )

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('admin:api:order-detail', kwargs={'pk': obj.pk})


class InvoiceSerializerMixin(vendor_mixins.PriceSerializerMixin, utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the invoice model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    order = OrderSerializerMixin(
        read_only=True
    )

    offer = OfferSerializerMixin(
        read_only=True
    )

    type_display = serializers.CharField(
        source='get_type_display',
        read_only=True
    )

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = customer_models.Invoice
        fields = '__all__'
        read_only_fields = ('id', 'annual_figure', 'is_deleted', 'deleted_at', 'created_date', 'updated_date')


class WalletSerializerMixin(customer_mixins.WalletSerializerMixin):
    """
    This class can handle the add and modify functions of the wallet model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    customer_id = serializers.CharField(
        source='customer.user',
        read_only=True
    )

    customer_name = serializers.CharField(
        source='customer.user.get_full_name',
        read_only=True
    )

    customer_email = serializers.CharField(
        source='customer.user.email',
        read_only=True
    )

    absolute_url = serializers.SerializerMethodField(
        source='get_absolute_url',
        read_only=True
    )

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('admin:api:wallet-detail', kwargs={'pk': obj.pk})


class DepositSerializerMixin(utils_serializers.Serializer):
    """
    This class is used to withdraw an amount from the user's wallet.
    where the value to be withdrawn is passed,
    it must be a valid value in order to complete the operation.
    """

    user = serializers.HiddenField(
        default=auth_mixins.CurrentUserDefault(),
        write_only=True
    )

    amount = serializers.FloatField(
        label=_('قيمة الإيداع'),
        validators=[MinValueValidator(1.0)]
    )

    def create(self, validated_data):
        """
        this function  is used to create offer code
        @param validated_data: the data we pass to offer
        @return: object
        """

        wallet = validated_data.pop('wallet')
        amount = validated_data.pop('amount')
        customer = wallet.customer
        response = wallet.deposit(amount=amount, **validated_data)
        signals.deposit_wallet.send(sender=wallet.__class__, user=customer.user, amount=amount)
        return response


class WithdrawSerializerMixin(DepositSerializerMixin):
    """
    This class is used to deposit an amount into the private wallet
    where the value to be deposited is passed, it must be a valid value in order to complete the operation
    """

    def create(self, validated_data):
        """
        this function  is used to create offer code
        @param validated_data: the data we pass to offer
        @return: object
        """
        wallet = validated_data.pop('wallet')
        amount = validated_data.pop('amount')
        customer = wallet.customer
        response = wallet.withdraw(amount=amount, **validated_data)
        signals.withdraw_wallet.send(sender=wallet.__class__, user=customer.user, amount=amount)
        return response


class NotificationSerializerMixin(serializers.Serializer):
    """
    This class is used to send notifications to registered users.
    the user type is passed along with the message header and body.
    """

    role = serializers.CharField(
        label=_('نوع المستخدم'),
        required=False,
        max_length=20,
    )

    subject = serializers.CharField(
        label=_('عنوان الرسالة'),
        required=False,
        max_length=200,
    )

    body = serializers.CharField(
        label=_('الرسالة'),
        required=False,
        max_length=None,
    )

    def create(self, validated_data):
        """
        This function is used to create notification
        @param validated_data: the data we pass to notification
        @return: validated_data
        """

        role = validated_data.get('role', None)
        body = validated_data.get('body', '')
        recipients = USER_MODEL.user_objects.all()

        if role is not None:
            recipients = recipients.filter(role=role)

        recipients = list(recipients.values_list('pk', flat=True))
        tasks.send_push_message_task.delay(recipients, body)
        return validated_data
