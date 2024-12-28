import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_unicode_slug, RegexValidator, MinLengthValidator, FileExtensionValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from django_resized import ResizedImageField
from phonenumber_field.modelfields import PhoneNumberField
from taggit.models import TagBase, GenericTaggedItemBase
from tinymce.models import HTMLField

from activatedapp.models import ActivatedModel
from utils.upload import image_folder, file_folder
from utils.validators import alpha
from . import managers


class Phone(models.Model):
    """
    This model is used to store phone data in the database.
    There are several types of phone, including HOME, WORK, FAX, and others.
    """

    class PhoneTypeChoices(models.TextChoices):
        HOME = 'H', _('رقم المنزل')
        WORK = 'W', _('رقم العمل')
        MOBILE = 'M', _('رقم الهاتف')
        FAX = 'F', _('رقم الفاكس')

    number = PhoneNumberField()

    phone_type = models.CharField(
        _('نوع الهاتف'),
        max_length=1,
        choices=PhoneTypeChoices.choices,
        default=PhoneTypeChoices.MOBILE
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )

    object_id = models.PositiveBigIntegerField()

    phone_object = GenericForeignKey()

    verified = models.BooleanField(
        verbose_name=_('التحقق'),
        default=False
    )

    primary = models.BooleanField(
        verbose_name=_('أساسي'),
        default=False
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    objects = managers.PhoneManager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('رقم الهاتف')
        verbose_name_plural = _('ارقام الهواتف')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return getattr(self.number, 'as_e164')


class Picture(models.Model):
    """
    This model is used to store phone data in the database.
    There are several types of phone, including fixed cellular, fax, and others ...
    """

    class PictureTypeChoices(models.TextChoices):
        PROFILE_PICTURE = 'PP', _('صورة الملف الشخصي')
        COVER_PICTURE = 'CP', _('صورة الغلاف')
        VIEW = 'VW', _('صورة العرض')

    picture_type = models.CharField(
        _('نوع الصورة'),
        max_length=2,
        choices=PictureTypeChoices.choices,
        default=PictureTypeChoices.VIEW
    )

    picture_file = ResizedImageField(
        quality=95,
        upload_to=image_folder
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    object_id = models.PositiveBigIntegerField()

    picture_object = GenericForeignKey()

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True)

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    objects = managers.PictureManager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('الصورة')
        verbose_name_plural = _('الصور')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return self.picture_file.name

    def get_image_url(self):
        """
        this function is return the full path of image
        @return: url
        """
        return hasattr(self.picture_file, 'url') if self.picture_file else None


class File(models.Model):
    """
    This class is used to store files data associated with other tables
    """

    file = models.FileField(
        verbose_name=_("الملف"),
        upload_to=file_folder,
        validators=[FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])]
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )

    object_id = models.PositiveBigIntegerField()

    file_object = GenericForeignKey()

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('الملف')
        verbose_name_plural = _('الملفات')

    def __str__(self):
        return self.file.name

    @property
    def get_file_url(self):
        """
        This method is used to return the full link of the file associated with the object.
        @return: The url of file.
        """
        return getattr(self.file, 'url') if self.file else None

    @property
    def extension(self):
        """
        this function is used to get file extension
        :return: extension
        """
        extension = os.path.splitext(self.file.name)[1]
        return extension

    @property
    def name(self):
        """
        this function is used to get file name
        :return: name
        """
        return os.path.basename(self.file.name)

    @property
    def size(self):
        """
        this function is used to get file size
        :return: size
        """
        return self.file.size


class City(ActivatedModel):
    """
    This class is used to represent the names of cities
    He has a one-to-many relationship with the table of countries
    """

    name = models.CharField(
        _('المدينة'),
        unique=True,
        max_length=255,
        error_messages={'unique': _('إسم المدينة موجود مسبقاً')},
    )

    code = models.CharField(
        _('الكود'),
        unique=True,
        max_length=155,
        error_messages={'unique': _('الكود موجود مسبقاً')},
        validators=[
            RegexValidator(
                regex=alpha,
                message=_('يسمح فقط بإدخال احرف انجليزية.'),
            ),
            MinLengthValidator(2),
        ]
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

    country = CountryField(default='SA')

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('المدينة')
        verbose_name_plural = _('المدن')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return self.name


class Policies(ActivatedModel):
    """
    This model is used to store privacy policies and terms and conditions
    """
    title = models.CharField(
        _('العنوان'),
        max_length=255,
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

    content = HTMLField()

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('صفحات سياسة الخصوصية')
        verbose_name_plural = _('صفحات سياسات الخصوصية')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return self.title
