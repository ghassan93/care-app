from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.views import PasswordContextMixin as AuthPasswordContextMixin

from rest_framework import serializers

from utils import serializers as utils_serializers, fields as utils_fields
from adminapp import models as admin_models
from vendorapp import models as vendor_models, signals as vendor_signals
from customerapp import models as customer_models

from . import forms, models, tasks

USER_MODEL = get_user_model()


class PasswordContextMixin(AuthPasswordContextMixin):
    validlink = False
    user = None
    code = None


class CurrentUserDefault:
    """
    This class used to return user object form http request
    """

    requires_context = True

    def __call__(self, serializer_field):
        """
        method enables Python programmers to write classes where the instances
        behave like functions and can be called like a function.
        :return: user object
        """
        user = serializer_field.context['request'].user
        return user

    def __repr__(self):
        """
        special methods are a set of predefined methods used to enrich your classes.
        They start and end with double underscores.
        :return:
        """
        return '%s()' % self.__class__.__name__


class UsernameSerializerMixin(serializers.Serializer):
    """
    This class is used to return the username field
    """

    username = serializers.CharField(
        label=_('إسم المستخدم'),
        max_length=settings.ACCOUNT_EMAIL_MAX_LENGTH,
        min_length=settings.ACCOUNT_USERNAME_MIN_LENGTH,
    )


class EmailSerializerMixin(serializers.Serializer):
    """
    This class is used to return the email field
    """

    email = utils_fields.EmailField(
        label=_("البريد الإلكتروني"),
    )


class RoleSerializerMixin(serializers.Serializer):
    """
    This class is used to return the role field
    """

    role = serializers.ChoiceField(
        label=_('نوع المستخدم'),
        choices=USER_MODEL.RoleChoices.choices
    )


class CodeSerializerMixin(serializers.Serializer):
    """
    This class is used to return the code field
    """

    code = serializers.CharField(
        label=_("رمز التحقق"),
        max_length=settings.ACCOUNT_CODE_MAX_LENGTH,
        min_length=settings.ACCOUNT_CODE_MIN_LENGTH
    )


class LoginSerializerMixin(UsernameSerializerMixin, RoleSerializerMixin, utils_serializers.FormSerializer):
    """
    This class is used to verify the username with the password.
    and it's used to log in user to the system.
    """

    password = serializers.CharField(
        label=_('كلمة المرور'), write_only=True,
        max_length=settings.ACCOUNT_PASSWORD_MAX_LENGTH,
        min_length=settings.ACCOUNT_PASSWORD_MIN_LENGTH,
        style={'input_type': 'password'}
    )

    remember = serializers.BooleanField(
        label=_('تذكرني'), write_only=True, default=False,
        style={'input_type': 'checkbox'}
    )

    form_class = forms.LoginForm

    def get_form_class(self, attrs):
        """
        This function is used to initialize the form data
        """
        request = self.context['request']
        return self.form_class(data=attrs, request=request)

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        return self.form.login()


class PasswordSerializerMixin(EmailSerializerMixin, RoleSerializerMixin, utils_serializers.FormSerializer):
    """
    This class is used to deal with the required password information
    that is shared among a group of other classes.
    """


class PasswordResetSerializerMixin(PasswordSerializerMixin):
    """
    This class is used to reset a user's password. Where he must enter the user's email and role,
    and then this class verifies the information and sends an alert to the e-mail
    associated with this user
    """

    form_class = forms.ResetPasswordForm

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        request = self.context['request']
        return self.form.save(request)


class PasswordCheckOTPSerializerMixin(CodeSerializerMixin, PasswordSerializerMixin):
    """
    This class is used to verify the code sent to the email.
    Where the e-mail, user role and code are entered,
    and then this class verifies the validity of the data.
    """

    form_class = forms.BasePasswordCheckOTPForm


class SetPasswordSerializerMixin(PasswordCheckOTPSerializerMixin):
    """
    This class is used to assign a new password by entering the user's email address,
    role, and verification code with the new password
    """

    new_password1 = utils_fields.PasswordField(
        label=_("كلمة المرور الجديدة")
    )

    new_password2 = utils_fields.PasswordField(
        label=_("تأكيد كلمة المرور الجديدة")
    )

    form_class = forms.SetPasswordForm


class UsernameChangeSerializerMixin(UsernameSerializerMixin, utils_serializers.FormSerializer):
    """
    This class is used to modify the username by passing the current user
    with the new username.
    """

    form_class = forms.ChangeUsernameForm

    def get_form_class(self, attrs):
        """
        This function is used to initialize the form data
        """
        user = self.context['user']
        return self.form_class(data=attrs, user=user)

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


class EmailChangeSerializerMixin(PasswordSerializerMixin):
    """
    This class is used to modify the username by passing the current user
    with the new username.
    """

    form_class = forms.ChangeEmailForm

    def get_form_class(self, attrs):
        """
        This function is used to initialize the form data
        """
        user = self.context['user']
        return self.form_class(data=attrs, user=user)

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called call
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        request = self.context['request']
        return self.form.save(request)


class PasswordChangeSerializerMixin(utils_serializers.FormSerializer):
    """
    This class is used to modify a user's password.
    Where the old password is entered with the new password and confirm password
    """

    oldpassword = utils_fields.PasswordField(
        label=_("كلمة المرور الحالية")
    )

    password1 = utils_fields.PasswordField(
        label=_("كلمة المرور الجديدة")
    )

    password2 = utils_fields.PasswordField(
        label=_("تأكيد كلمة المرور الجديدة")
    )

    form_class = forms.ChangePasswordForm

    def get_form_class(self, attrs):
        """
        This function is used to initialize the form data
        """
        user = self.context['user']
        return self.form_class(data=attrs, user=user)


class ProfileSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the profile model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    city = serializers.SlugRelatedField(
        label=_('المدينة'),
        slug_field='slug',
        queryset=admin_models.City.activated.all()
    )

    city_display = serializers.CharField(
        source='city.name',
        read_only=True
    )

    gender_display = serializers.CharField(
        source='get_gender_display',
        read_only=True
    )

    image_file = serializers.ImageField(
        required=False,
        write_only=True
    )

    cover_file = serializers.ImageField(
        required=False,
        write_only=True
    )

    image = serializers.URLField(
        source='get_image_url',
        read_only=True
    )

    cover = serializers.URLField(
        source='get_cover_url',
        read_only=True
    )

    class Meta:
        abstract = True
        model = models.Profile
        exclude = ('user',)


class AddressSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the address model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    user = serializers.HiddenField(
        default=CurrentUserDefault(),
        write_only=True
    )

    class Meta:
        abstract = True
        model = models.Address
        fields = '__all__'
        read_only_fields = ('is_active', 'activated_at', 'disabled_at', 'created_date', 'updated_date')


class WalletSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the wallet model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    balance_display = serializers.CharField(
        source='get_balance_display',
        read_only=True
    )

    class Meta:
        abstract = True
        model = customer_models.Wallet
        fields = '__all__'
        read_only_fields = (
            'is_active', 'activated_at', 'disabled_at', 'is_deleted', 'deleted_at', 'created_date', 'updated_date'
        )


class UserSerializerMixin(EmailSerializerMixin, utils_serializers.ModelSerializer, utils_serializers.FormSerializer):
    """
    This class can handle the add and modify functions of the user model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    profile = ProfileSerializerMixin(
        label=_('الملف الشخصي'),
    )

    wallet = WalletSerializerMixin(
        source='customer.wallet',
        read_only=True,
    )

    password1 = utils_fields.PasswordField(
        label=_('كلمة المرور'),
        write_only=True
    )

    password2 = utils_fields.PasswordField(
        label=_('تأكيد كلمة المرور'),
        write_only=True
    )

    addresses = AddressSerializerMixin(
        many=True,
        read_only=True
    )

    full_name = serializers.CharField(
        source='get_full_name',
        read_only=True
    )

    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True
    )

    verified_email = serializers.BooleanField(
        source='is_verified_email',
        read_only=True
    )

    verified_phonenumber = serializers.BooleanField(
        source='is_verified_phonenumber',
        read_only=True
    )

    form_class = forms.RegisterForm

    class Meta:
        abstract = True
        model = USER_MODEL
        exclude = ('password', 'groups', 'user_permissions', 'is_superuser', 'is_staff')
        read_only_fields = (
            'role', 'slug', 'verified_email_at', 'verified_phonenumber_at', 'is_active', 'activated_at', 'disabled_at',
            'is_deleted', 'deleted_at', 'date_joined', 'updated_date', 'last_login'
        )
        extra_kwargs = {'username': {'required': False}}

    def validate(self, attrs):
        """

        @param attrs:
        @return:
        """
        if not self.instance:
            return super(UserSerializerMixin, self).validate(attrs)
        return attrs

    def get_form_class(self, attrs):
        """
        This function is used to initialize the form data
        """
        role = self.context['role']
        return self.form_class(role=role, data=attrs)

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
        profile_data = validated_data.pop('profile', None)
        if profile_data:
            self.fields["profile"].update(instance.profile, profile_data)
        return super(UserSerializerMixin, self).update(instance, validated_data)

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        request = self.context['request']
        profile = validated_data.pop('profile', None)
        instance = self.form.save(request, **validated_data)
        if profile is not None:
            self.fields["profile"].update(instance.profile, profile)
        return instance


class VendorSerializerMixin(serializers.ModelSerializer):
    """
    This class is used to register the vendor model in database.
    """

    user = UserSerializerMixin(
        write_only=True
    )

    city = serializers.SlugRelatedField(
        label=_('المدينة'),
        slug_field='slug',
        queryset=admin_models.City.activated.all()
    )

    tags = utils_fields.TagListSerializerField(
        label=_('الفئات'),
        required=False,
        slug_field='name',
        queryset=vendor_models.Tag.activated.all()
    )

    class Meta:
        abstract = True
        model = vendor_models.Vendor
        fields = '__all__'
        read_only_fields = (
            'slug', 'payment_type', 'parent', 'lft', 'rght', 'tree_id', 'level', 'rate', 'is_active',
            'activated_at', 'disabled_at', 'is_deleted', 'deleted_at', 'updated_date', 'created_date'
        )

    def get_user_serializer_class(self):
        """
        this class is used to return user serializer class
        @return: serializer
        """
        serializer = self.fields["user"]
        serializer._context.update({'request': self.context['request'], 'role': USER_MODEL.RoleChoices.VENDOR})
        return serializer

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

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        user_data = validated_data.pop('user', None)
        tags_data = validated_data.pop('tags', [])
        vendor = super(VendorSerializerMixin, self).create(validated_data)
        user = self.get_user_serializer_class().create(user_data)
        vendor_signals.create_vendor.send(sender=vendor.__class__, vendor=vendor, user=user)
        vendor.tags.add(*tags_data)
        return user


class EmailCheckOTPSerializerMixin(PasswordCheckOTPSerializerMixin):
    """
    This class is used to verify the code sent to the email.
    Where the e-mail, user role and code are entered,
    and then this class verifies the validity of the data.
    """


class ResenActivateEmailSerializerMixin(PasswordResetSerializerMixin):
    """
    This class is used to resend the verification code to the e-mail
    by passing the e-mail with the user's roller
    """

    form_class = forms.ResendActivateEmail


class ActivateEmailSerializerMixin(PasswordCheckOTPSerializerMixin):
    """
    This class is used to activate the user's e-mail by passing the e-mail and
    the user's roll with the code sent to the e-mail
    """

    form_class = forms.ActivateEmail


class UserDeletionSerializerMixin(utils_serializers.ModelSerializer):
    """
    This class can handle the add and modify functions of the user deletion model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    user = serializers.HiddenField(
        default=CurrentUserDefault(),
        write_only=True
    )

    class Meta:
        abstract = True
        model = models.UserDeletion
        fields = '__all__'
        read_only_fields = ('is_active', 'activated_at', 'disabled_at', 'created_date', 'updated_date')


class UserNotificationSerializerMixin(serializers.Serializer):
    """
    This class can handle the add and modify functions of the actor notification model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    username = serializers.CharField()

    full_name = serializers.CharField(
        source='get_full_name'
    )

    image = serializers.CharField(
        source='profile.get_image_url'
    )


class GenericNotificationRelatedFieldMixin(serializers.RelatedField):
    """
    This field is used to represent the notifications associated
    with the user and return them to the serializer class
    """

    def to_representation(self, value):
        """
        Object instance -> Dict of primitive datatypes.
        """

        if isinstance(value, USER_MODEL):
            serializer = UserNotificationSerializerMixin(value)

        return serializer.data


class NotificationSerializerMixin(RoleSerializerMixin):
    """
    This class can handle the add and modify functions of the notification model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations.
    And class is used to send notifications to users by passing the user's roll
    with the letter address and the text of the message.
    where these classes use the Expo to send notifications
    """

    subject = serializers.CharField(
        label=_('عنوان الرسالة'),
        required=False,
        max_length=200,
        write_only=True
    )

    body = serializers.CharField(
        label=_('الرسالة'),
        required=False,
        max_length=None,
        write_only=True
    )

    actor = GenericNotificationRelatedFieldMixin(
        read_only=True
    )

    pk = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    unread = serializers.BooleanField(
        read_only=True
    )

    description = serializers.CharField(
        read_only=True
    )

    timestamp = serializers.DateTimeField(
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
        super(NotificationSerializerMixin, self).__init__(*args, **kwargs)
        self.fields['role'].write_only = True

    def get_absolute_url(self, obj):
        """
        This function is used ro return absolute url for object
        @param obj: the custom object
        @return: url
        """
        return reverse('auth:api:notification-detail', kwargs={'pk': obj.pk})

    def create(self, validated_data):
        """
        This function is used to create notification
        @param validated_data: the data we pass to notification
        @return: validated_data
        """

        role = validated_data.get('role', None)
        body = validated_data.get('body', '')
        recipients = get_user_model().user_objects.all()

        if role is not None:
            recipients = recipients.filter(role=role)

        recipients = list(recipients.values_list('pk', flat=True))
        tasks.send_push_message_task.delay(recipients, body)
        return validated_data


class ExpoPushTokenSerializerMixin(utils_serializers.FormSerializer):
    """
    This class can handle the add and modify functions of the expo push token model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """

    exponent_push_token = serializers.CharField(
        label=_('رمز ألتوكن الخاص بالمستخدم'),
        required=settings.EXPO_PUSH_TOKEN_REQUIRED,
        max_length=settings.EXPO_PUSH_TOKEN_MAX_LENGTH,
        min_length=settings.EXPO_PUSH_TOKEN_MIN_LENGTH,
    )

    form_class = forms.ExpoPushTokenForm

    def create(self, validated_data):
        """
        This function is used to create a new object from
        a specific form where this function is called
        to check the input check.
        This function restarts the created object in this function.
        @param validated_data: the data that pass to function.
        @return: Object of the model.
        """
        request = self.context['request']
        return self.form.save(request)
