import pytz
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator, validate_unicode_slug
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django_resized import ResizedImageField
from django_softdelete.models import SoftDeleteModel
from phonenumber_field.modelfields import PhoneNumberField

from activatedapp.models import ActivatedModel
from utils.upload import image_folder
from utils.validators import ASCIIUsernameValidator
from adminapp import models as admin_model
from . import managers


class User(AbstractUser, ActivatedModel, SoftDeleteModel):
    """
    Users within the Django authentication system are represented by this
    model.
    email, phonenumber and password are required. Other fields are optional.
    """

    username_validator = ASCIIUsernameValidator()

    class RoleChoices(models.TextChoices):
        """
        This class contains user types such as Admin, Vendor or Customer
        """
        ADMIN = 'admin', _('مدير')
        VENDOR = 'vendor', _('بائع')
        CUSTOMER = 'customer', _('عميل')

    username = models.CharField(
        _('إسم المستخدم'),
        max_length=settings.ACCOUNT_USERNAME_MAX_LENGTH,
        unique=True,
        help_text=_('مطلوب. 150 حرفًا أو أقل. المسموح كتابة أحرف اوأرقام او @ /. / + / - / _ فقط.'),
        validators=[username_validator],
        error_messages={'unique': _('اسم المستخدم موجود مسبقا.')},

    )

    email = models.EmailField(
        _('البريد الإلكتروني'),
        validators=[EmailValidator()]
    )

    phonenumber = PhoneNumberField(
        verbose_name=_('رقم الهاتف')
    )

    role = models.CharField(
        _('نوع المستخدم'),
        max_length=30,
        choices=RoleChoices.choices
    )

    slug = models.SlugField(
        _('الرابط'),
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        editable=False,
        validators=[validate_unicode_slug],
    )

    verified_email_at = models.DateTimeField(
        _('تاريخ تفعيل البريد الإلكتروني'),
        null=True
    )

    verified_phonenumber_at = models.DateTimeField(
        _('تاريخ تفعيل الهاتف'),
        null=True
    )

    allow_notification = models.BooleanField(
        _('السماح بالإشعارات'),
        default=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    objects = managers.UserManager()
    user_objects = managers.UserUndeletedManager()

    class Meta:
        unique_together = [['email', 'role']]
        ordering = ['-id']
        verbose_name = _('المستخدم')
        verbose_name_plural = _('المستخدمين')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'@{self.username}'

    @property
    def is_verified(self):
        """
        this function is check if user activated and not deleted
        @return: Boolean
        """
        return bool(
            self.is_active and
            not self.is_deleted and
            (self.vendor_user.is_verified if self.role == self.RoleChoices.VENDOR else True)
        )

    @property
    def is_admin(self):
        """
        A method used to check if an object is an Admin or not.
        @return: True if role equal 'admin' else False.
        """
        return self.role == self.RoleChoices.ADMIN and self.is_superuser and self.is_staff and self.is_verified

    @property
    def is_vendor(self):
        """
        A method used to check if an object is a Vendor or not.
        @return: True if role equal 'vendor' else False.
        """
        return self.role == self.RoleChoices.VENDOR and self.is_verified

    @property
    def is_customer(self):
        """
        A method used to check if an object is a Customer or not.
        @return: True if role equal 'customer' else False.
        """
        return self.role == self.RoleChoices.CUSTOMER and self.is_verified

    def set_role(self, role):
        """
        A method used to assign a user type to an object
        @param role: user type such as Admin, Supervisor or Investor
        """
        self.is_superuser = False
        self.is_staff = False

        if role == self.RoleChoices.ADMIN:
            self.is_superuser = True
            self.is_staff = True

        self.role = role

    def change_email(self, email):
        """
        this function used to change email of the user
        @param email: the new email
        @return: None
        """
        self.email = email
        self.verified_email_at = None
        self.save()

    def change_phonenumber(self, phonenumber):
        """
        this function used to change phonenumber of the user
        @param phonenumber: the new phonenumber
        @return: None
        """
        self.phonenumber = phonenumber
        self.verified_phonenumber_at = None
        self.save()

    def activate_email(self):
        """
        his function used to activate email of the user
        @return: None
        """
        self.verified_email_at = timezone.now()
        self.save()

    def activate_phonenumber(self):
        """
        his function used to activate phonenumber of the user
        @return: None
        """
        self.verified_phonenumber_at = timezone.now()
        self.save()

    def make_allow_notification(self):
        """
        Activate notifications for the user
        @return: None
        """
        self.allow_notification = True
        self.save()

    def make_disallow_notification(self):
        """
        Disallow notifications for the user
        @return: None
        """
        self.allow_notification = False
        self.save()

    def is_verified_email(self):
        """
        check if email is verified
        @return: Boolean
        """
        return bool(self.verified_email_at)

    def is_verified_phonenumber(self):
        """
        check if phonenumber is verified
        @return: Boolean
        """
        return bool(self.verified_phonenumber_at)

    def block(self):
        """
        this function is used to block the user
        @return: None
        """
        self.is_active = False
        self.save()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    PHONENUMBER_FILED = 'phonenumber'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'phonenumber']


class Profile(models.Model):
    """
    This class represents additional information about the user
    as it has a one-to-one relationship with the user class
    """

    class GenderChoices(models.TextChoices):
        """
        This class contains Gender such as Male or Female
        """
        MALE = 'male', _('ذكر')
        FEMALE = 'female', _('انثى')

    gender = models.CharField(
        _('الجنس'),
        max_length=6,
        choices=GenderChoices.choices,
        default=GenderChoices.MALE
    )

    birthdate = models.DateField(
        _('تاريخ الميلاد'),
        null=True,
        blank=True
    )

    image_file = ResizedImageField(
        verbose_name=_('صورة المستخدم'),
        quality=100,
        upload_to=image_folder,
        blank=True
    )

    cover_file = ResizedImageField(
        verbose_name=_('صورة الغلاف'),
        quality=100,
        upload_to=image_folder,
        blank=True
    )

    summary = models.TextField(
        _('ملخص'),
        blank=True
    )

    timezone = models.CharField(
        _('نوع التاريخ'),
        max_length=40,
        default='Asia/Riyadh',
        choices=[(n, n) for n in pytz.all_timezones]
    )

    location = models.TextField(
        _('الموقع'),
        blank=True,
        null=True
    )

    latitude = models.FloatField(
        _('خط العرض'),
        blank=True,
        null=True
    )

    longitude = models.FloatField(
        _('خط الطول'),
        blank=True,
        null=True
    )

    city = models.ForeignKey(
        admin_model.City,
        related_name='profile',
        on_delete=models.SET_NULL,
        null=True
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('المستخدم'),
        on_delete=models.CASCADE,
        related_name='profile'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('الملف الشخصي')
        verbose_name_plural = _('الملف الشخصي')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return self.user.__str__()

    @property
    def get_image_url(self):
        """
        This method is used to return the full link of the image associated with the user.
        @return: The url of Image.
        """
        return getattr(self.image_file, 'url') if self.image_file else settings.DEFAULT_IMAGE

    @property
    def get_cover_url(self):
        """
        This method is used to return the full link of the image associated with the user.
        @return: The url of Image.
        """
        return getattr(self.cover_file, 'url') if self.cover_file else ''


class Address(ActivatedModel):
    """
    This class is used to save address information for the user,
    where the user can add more than one address
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='addresses',
        on_delete=models.CASCADE
    )

    title = models.CharField(
        _('عنوان الموقع'),
        max_length=150
    )

    location = models.TextField(
        _('الموقع')
    )

    latitude = models.FloatField(
        _('خط العرض')
    )

    longitude = models.FloatField(
        _('خط الطول')
    )

    objects = managers.AddressManager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('العنوان')
        verbose_name_plural = _('العنوان')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return self.user.__str__()


class UserDeletion(ActivatedModel):
    """
    This class is used to save requests from users who want
    to delete their data from the system
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='deletion',
        on_delete=models.CASCADE
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    class Meta:
        default_permissions = ()
        ordering = ['-id']
        verbose_name = _('طلبات الحذف')
        verbose_name_plural = _('طلبات الحذف')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return self.user.__str__()


class ExponentPushToken(ActivatedModel):
    """
    These classes are used to store the Token value of your user phone.
    it's used to send notification code to user mobile.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='token',
        on_delete=models.CASCADE
    )

    receiver_token = models.CharField(
        _('توكن المستلم'),
        max_length=settings.EXPO_PUSH_TOKEN_MAX_LENGTH
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    objects = managers.ExponentPushTokenManager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('كود الجوال')
        verbose_name_plural = _('كود الجوال')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return self.user.__str__()
