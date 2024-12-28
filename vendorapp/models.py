from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import (
    validate_unicode_slug, FileExtensionValidator,
    MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator, RegexValidator
)
from django.db import models
from django_resized import ResizedImageField
from django.utils.translation import ugettext_lazy as _
from django_softdelete.models import SoftDeleteModel
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from sort_order_field import SortOrderField
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase
from activatedapp.models import ActivatedModel
from utils.slug import unique_slug_generator
from utils.time2word import Time2Word
from utils.upload import file_folder, image_folder
from adminapp import models as admin_model
from utils.validators import alphanumeric

from . import managers, shortcut

USER_MODEL = get_user_model()


def hours_choices():
    return [(r, r) for r in range(13)]


def minutes_choices():
    return [(r, r) for r in range(0, 46, 15)]


class VendorTypeChoice(models.TextChoices):
    """
    This class contains service type such as Male or Female
    """
    SELF_CARE = 'self-care', _('العناية بالجمال')
    CAR_CARE = 'car-care', _('العناية بالسيارة')


class Comment(MPTTModel, ActivatedModel):
    """
    This model is used to store comment data and rates in the database.
    """

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    rate = models.FloatField(
        _('التقييم'),
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]

    )

    content = models.TextField(
        _('محتوى التعليق'),
        blank=True,
        null=True
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment'
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )

    object_id = models.PositiveBigIntegerField()

    comment_object = GenericForeignKey()

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
        verbose_name = _('التعليقات')
        verbose_name_plural = _('التعليقات')


class Tag(TagBase, ActivatedModel):
    """
    This class is used to activate the tag feature on different models
    """

    tag_type = models.CharField(
        _('نوع الفئة'),
        max_length=20,
        choices=VendorTypeChoice.choices,
        null=True,
        blank=True
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
        ordering = ['-id']
        verbose_name = _('الفئة')
        verbose_name_plural = _('الفئات')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.name}'

    def slugify(self, tag, i=None):
        """
        this function is used to slugify tag name its uses as identifier in the usr
        @param tag: the tag name
        @param i:
        @return: slugify
        """
        return unique_slug_generator(instance=self, new_slug=tag)


class TaggedItem(GenericTaggedItemBase):
    """
    This class is used to activate the tag feature on different models
    """

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_items',
    )

    class Meta:
        verbose_name = _('Tagged Item')
        verbose_name_plural = _('Tagged Items')
        index_together = [['content_type', 'object_id']]


class Vendor(MPTTModel, ActivatedModel, SoftDeleteModel):
    """
    This class is used to store the vendor's information in the database,
    where each seller has the name of the business, the type of vendor,
    the place of work and other information shown in this model
    """

    class PlaceChoices(models.TextChoices):
        """
        This class contains allowed such as Male or Female
        """
        HOME = 'home', _('المنزل')
        SHOP = 'shop', _('المحل')
        ALL = 'all', _('كليهما')

    class AllowedChoices(models.TextChoices):
        """
        This class contains allowed such as Male or Female
        """
        MALES = 'males', _('ذكور')
        FEMALES = 'females', _('إناث')
        ALL = 'all', _('الكل')

    class StatusChoices(models.TextChoices):
        """
        This class contains availability such as open or close
        """
        OPEN = 'open', _('متاح')
        CLOSE = 'close', _('مغلق')

    class PaymentTypeChoices(models.TextChoices):
        """
        This class contains availability such as open or close
        """
        SYSTEM = 'system', _('الدفع من خلال النظام')
        VENDOR = 'vendor', _('الدفع من خلال البائع')

    parent = TreeForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )

    name = models.CharField(
        _('الاسم التجاري'),
        max_length=255
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

    vendor_type = models.CharField(
        _('نوع البائع'),
        max_length=20,
        choices=VendorTypeChoice.choices,
    )

    place = models.CharField(
        _('محل البيع'),
        max_length=20,
        choices=PlaceChoices.choices,
        default=PlaceChoices.SHOP
    )

    sort_order = SortOrderField(
        _("ترتيب البائع"),
        default=100,
        validators=[
            MinValueValidator(0)
        ]
    )

    city = models.ForeignKey(
        admin_model.City,
        related_name='vendor',
        on_delete=models.SET_NULL,
        null=True
    )

    street = models.CharField(
        _('الحي'),
        max_length=255,
        blank=True,
        null=True
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

    time_from = models.TimeField(
        _('وقت بداية الدوام'),
        null=True
    )

    time_to = models.TimeField(
        _('وقت نهاية الدوام'),
        null=True
    )

    pictures = GenericRelation(
        admin_model.Picture,
        related_query_name='pictures'
    )

    phones = GenericRelation(
        admin_model.Phone,
        related_query_name='phones'
    )

    tags = TaggableManager(through=TaggedItem)

    rate = models.FloatField(
        _('التقييم'),
        default=settings.DEFAULT_RATE_VALUE,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]
    )

    cr_no = models.PositiveBigIntegerField(
        _('رقم السجل التجاري'),
    )

    cr_file = models.FileField(
        verbose_name=_('ملف السجل التجاري'),
        upload_to=file_folder,
        validators=[FileExtensionValidator(['pdf', 'docx', 'doc', 'png', 'jpg'])],
        null=True,
        blank=True
    )

    payment_type = models.CharField(
        _('نوع الدفع'),
        max_length=20,
        choices=PaymentTypeChoices.choices,
        default=PaymentTypeChoices.SYSTEM
    )

    allowed = models.CharField(
        _('مسموح لكل من'),
        max_length=8,
        choices=AllowedChoices.choices,
        default=AllowedChoices.ALL
    )

    website = models.URLField(
        _('عنوان موقع الويب'),
        null=True,
        blank=True
    )

    description = models.TextField(
        _('وصف البائع'),
        null=True,
        blank=True
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    vendor_objects = managers.VendorManager()
    verified_objects = managers.VendorVerifiedManager()

    class Meta:
        ordering = ['sort_order', '-id']
        verbose_name = _('البائع')
        verbose_name_plural = _('البائعين')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.name}'

    @property
    def is_self_care(self):
        """
        check if vendor is self_care
        @return: Boolean
        """
        return self.vendor_type == VendorTypeChoice.SELF_CARE

    @property
    def is_car_care(self):
        """
        check if vendor is car_care
        @return: Boolean
        """
        return self.vendor_type == VendorTypeChoice.CAR_CARE

    @property
    def get_status_display(self):
        """
        this function is used to return the status of vendor
        @return: open or close
        """
        current_time = shortcut.current_datetime().time()

        if shortcut.time_in_range(self.time_from, self.time_to, current_time):
            return self.StatusChoices.OPEN.label

        return self.StatusChoices.CLOSE.label

    def get_users(self):
        """
        this function is used ro return all users for custom vendor
        """
        return USER_MODEL.user_objects.users_for_vendor(self)

    def get_sales(self):
        """
        this function is used to return all sales for vendor
        @return: Queryset
        """
        return Service.sales_objects.all_sales(self)

    def get_employees(self):
        """
        this function is used to return all employees for vendor
        @return: Queryset
        """
        return Employee.verified_objects.all_employees(self)

    def get_orders(self):
        """
        this function is used to return all employees for vendor
        @return: Queryset
        """
        from customerapp.models import Order
        return Order.verified_objects.all_vendor_orders(self)


class VendorUser(models.Model):
    """
    This class is used to connect users with vendor,
    where each vendor can have more than one user in the system,
    and this will support flexibility in the system.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_user'
    )

    is_manager = models.BooleanField(
        _('مدير'),
        default=False
    )

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='vendor_user'
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
        ordering = ['-id']
        verbose_name = _('المستخدمين للبائعين')
        verbose_name_plural = _('المستخدمين للبائعين')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.user.__str__()}'

    @property
    def is_verified(self):
        """
        check if vendor is active
        @return: boolean
        """
        return self.vendor.is_active


class Sales(models.Model):
    """
    This class is used to store customer services, and it consists of types,
    like Services and Products
    """

    vendor = models.ForeignKey(
        Vendor,
        related_name='sales',
        on_delete=models.CASCADE
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in': settings.CONTENT_MODEL_PROVIDER}
    )

    object_id = models.PositiveIntegerField()

    content_object = GenericForeignKey('content_type', 'object_id')

    created_date = models.DateTimeField(auto_now_add=True)

    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
        verbose_name = _('المبيعات')
        verbose_name_plural = _('المبيعات')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'sales {self.id}'


class PriceMethodsBase(models.Model):
    """
    This is abstract model  for handling the price attributes
    """

    class Meta:
        abstract = True

    @property
    def get_price_value(self):
        """
        This methode is used ro return tax
        @return: tax.
        """
        return getattr(self, 'price')

    @property
    def get_tax_value(self):
        """
        This methode is used ro return tax
        @return: tax.
        """
        return shortcut.get_tax_value(self.get_total_value_before_tax, getattr(self, 'tax'))

    @property
    def get_discount_value(self):
        """
        This methode is used ro return discount
        @return: discount.
        """
        return shortcut.get_discount_value(self.get_price_value, getattr(self, 'discount'))

    @property
    def get_total_value_before_tax(self):
        """
        This methode is used ro return total
        @return: total.
        """
        return shortcut.get_total_value_before_tax(self.get_price_value, self.get_discount_value)

    @property
    def get_total_value(self):
        """
        This methode is used ro return total
        @return: total.
        """

        return shortcut.get_total_value(self.get_total_value_before_tax, self.get_tax_value)

    @property
    def get_price_value_display(self):
        """
        This methode is used ro return price
        @return: price.
        """
        return shortcut.get_intcomma_display(self.get_price_value)

    @property
    def get_discount_percent_display(self):
        """
        This methode is used ro return discount
        @return: discount.
        """
        return f"{getattr(self, 'discount')}%"

    @property
    def get_discount_value_display(self):
        """
        This methode is used ro return discount
        @return: discount.
        """

        return shortcut.get_intcomma_display(getattr(self, 'get_discount_value'))

    @property
    def get_tax_percent_display(self):
        """
        This methode is used ro return discount
        @return: discount.
        """
        return f"{getattr(self, 'tax')}%"

    @property
    def get_tax_value_display(self):
        """
        This methode is used ro return discount
        @return: discount.
        """
        return shortcut.get_intcomma_display(getattr(self, 'get_tax_value'))

    @property
    def get_total_value_before_tax_display(self):
        """
        This methode is used ro return price
        @return: price.
        """
        return shortcut.get_intcomma_display(self.get_total_value_before_tax)

    @property
    def get_total_value_display(self):
        """
        This methode is used ro return price
        @return: price.
        """
        return shortcut.get_intcomma_display(self.get_total_value)


class PriceBase(PriceMethodsBase):
    """
    This is abstract model  for handling the price attributes
    """

    price = models.FloatField(
        _('السعر')
    )

    discount = models.FloatField(
        _('نسبة التخفيض'),
        default=0,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )

    tax = models.FloatField(
        _('نسبة الضريبة'),
        default=0,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )

    class Meta:
        abstract = True

    @property
    def total(self):
        """
        This methode is used ro return total
        @return: total.
        """
        return self.get_total_value


class SalesBase(PriceBase, ActivatedModel, SoftDeleteModel):
    """
    This class is base class, used to store customer services, products and other.
    """

    sales = GenericRelation(Sales, related_query_name='sales_base')

    name = models.CharField(
        _('إسم الخدمة'),
        max_length=255
    )

    slug = models.SlugField(
        _('الرابط'),
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        editable=False,
        validators=[validate_unicode_slug]
    )

    comment = GenericRelation(Comment, related_query_name='comments')

    tags = TaggableManager(through=TaggedItem)

    description = models.TextField(
        _('الوصف'),
        null=True,
        blank=True
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    objects = models.Manager()

    sales_objects = managers.SalesBaseManager()

    verified_objects = managers.VendorVerifiedManager()

    class Meta:
        ordering = ['-id']
        abstract = True

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.name}'

    def get_vendor(self):
        """
        This methode is used ro return vendor name
        @return: price.
        """
        sales = getattr(self, 'sales').first()

        if not sales:
            return None

        return sales.vendor

    def get_comment_objects(self):
        """
        this is function for _comments
        @return: return comments objects
        """""
        return self.comment.filter(is_active=True)

    @property
    def get_tax_value(self):
        """
        This methode is used ro return tax
        @return: tax.
        """
        return shortcut.get_tax_value(self.get_total_value_before_tax, settings.KSA_DEFAULT_TAX)

    @property
    def get_tax_percent_display(self):
        """
        This methode is used ro return discount
        @return: discount.
        """
        return f"{settings.KSA_DEFAULT_TAX}%"


class Service(SalesBase):
    """
    This class is used to store customer services
    """

    class ServiceTypeChoice(models.TextChoices):
        """
        This class contains service type such as Male or Female
        """
        SELF_MALE = 'self-care', _('العناية بالجمال')
        CAR_CARE = 'car-care', _('العناية بالسيارة')

    class PlaceChoices(models.TextChoices):
        """
        This class contains allowed such as Male or Female
        """
        HOME = 'home', _('المنزل')
        SHOP = 'shop', _('المتجر')

    class ScheduleTypeChoices(models.TextChoices):
        """
        This class contains allowed such as Male or Female
        """
        DEFAULT = 'default', _('افتراضية')
        UNSCHEDULED = 'unscheduled', _('غير مجدولة')

    hour = models.IntegerField(
        _('أجمالي الخدمة بالساعات'),
        choices=hours_choices()
    )

    minute = models.IntegerField(
        _('أجمالي الخدمة بالدقائق'),
        choices=minutes_choices()
    )

    type = models.CharField(
        _('نوع الخدمة'),
        max_length=20,
        choices=ServiceTypeChoice.choices,
    )

    place = models.CharField(
        _('مكان الخدمة'),
        max_length=20,
        choices=PlaceChoices.choices,
        default=PlaceChoices.SHOP
    )

    schedule = models.CharField(
        _('نوع الجدولة'),
        max_length=20,
        choices=ScheduleTypeChoices.choices,
        default=ScheduleTypeChoices.DEFAULT
    )

    image_file = ResizedImageField(
        verbose_name=_('صورة العرض'),
        quality=70,
        upload_to=image_folder,
        blank=True
    )

    sales = GenericRelation(Sales, related_query_name='services')

    comment = GenericRelation(Comment, related_query_name='services')

    class Meta:
        ordering = ['-id']
        verbose_name = _('الخدمة')
        verbose_name_plural = _('الخدمات')

    @property
    def get_time_display(self):
        """
        This methode is used ro return discount
        @return: discount.
        """
        return Time2Word(self.hour, self.minute).format()

    @property
    def get_image_url(self):
        """
        This method is used to return the full link of the image associated with the user.
        @return: The url of Image.
        """
        return getattr(self.image_file, 'url') if self.image_file else None

    @property
    def time(self):
        """
        this is property for time
        @return: return time delta to time
        """""
        return shortcut.time2delta(self)


class Product(SalesBase):
    """
    This class is used to store customer product.
    """

    service = models.ForeignKey(
        Service,
        related_name='product',
        on_delete=models.SET_NULL,
        null=True
    )

    brand = models.CharField(_('الماركة'), max_length=255, null=True, blank=True)

    wight = models.FloatField(
        _('الوزن'),
        default=0
    )

    specification = models.TextField(
        _('التخصص'),
        null=True,
        blank=True
    )

    pictures = GenericRelation(admin_model.Picture, related_query_name='pictures')

    sales = GenericRelation(Sales, related_query_name='products')

    comment = GenericRelation(Comment, related_query_name='products')

    class Meta:
        ordering = ['-id']
        verbose_name = _('المنتج')
        verbose_name_plural = _('المنتجات')


class Employee(SoftDeleteModel):
    """
    This class is used to store employee data.
    """

    vendor = models.ForeignKey(
        Vendor,
        related_name='employee',
        on_delete=models.CASCADE
    )

    name = models.CharField(
        _('إسم الموظف'),
        max_length=255
    )

    image_file = ResizedImageField(
        verbose_name=_('صورة العرض'),
        quality=70,
        upload_to=image_folder,
        blank=True
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    service = models.ManyToManyField(
        Service,
        through='Availability'
    )

    objects = models.Manager()

    verified_objects = managers.EmployeeManager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('الموظف')
        verbose_name_plural = _('الموظفين')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.name}'

    @property
    def get_image_url(self):
        """
        This method is used to return the full link of the image associated with the user.
        @return: The url of Image.
        """
        return getattr(self.image_file, 'url') if self.image_file else None


class Offer(ActivatedModel, SoftDeleteModel):
    """
    This class is used to store discount codes
    """

    class OfferTypeChoices(models.TextChoices):
        """
        This class contains allowed such as Male or Female
        """
        VENDOR = 'vendor', _('البائع')
        ADMIN = 'admin', _('النظام')

    vendor = models.ForeignKey(
        Vendor,
        related_name='offer',
        on_delete=models.SET_NULL,
        null=True
    )

    discount = models.FloatField(
        _('قيمة التخفيض'),
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ]
    )

    code = models.CharField(
        _('كود الخصم'),
        max_length=150,
        validators=[
            RegexValidator(
                regex=alphanumeric,
                message=_('يجب أن  يكون الكود مزيجًا من الأحرف الأبجدية والأرقام')
            ),
            MinLengthValidator(4),
            MaxLengthValidator(12)
        ]
    )

    type = models.CharField(
        _('نوع الخصم'),
        max_length=20,
        choices=OfferTypeChoices.choices,
    )

    uses = models.IntegerField(
        _('عدد الاستخدامات'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(1000)
        ]
    )

    expire_date = models.DateField(
        _('تاريخ الانتهاء')
    )

    is_active = models.BooleanField(
        _('تم التفعيل'),
        default=False
    )

    users = models.ManyToManyField(
        USER_MODEL
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    offer_objects = managers.OfferManager()

    verified_objects = managers.OfferVerifiedManager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('أكواد الخصم')
        verbose_name_plural = _('أكواد الخصم')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.code}'

    @property
    def get_users_count(self):
        """
        this function return all users that used this code.
        @return: int
        """
        return getattr(self, 'users').all().count()

    @property
    def is_valid_counts(self):
        """
        this function is uses to validate uses offer code
        @return:
        """
        return self.get_users_count < self.uses


class Banner(ActivatedModel):
    """
    This model is used to store phone data in the database.
    There are several types of phone, including fixed cellular, fax, and others ...
    """

    vendors = models.ManyToManyField(
        Vendor()
    )

    banner_type = models.CharField(
        _('نوع اللافتة'),
        max_length=20,
        choices=VendorTypeChoice.choices,
        null=True
    )

    subject = models.CharField(
        _('عنوان اللافتة'),
        max_length=155,
        blank=True
    )

    body = models.CharField(
        _('موضوع اللافتة'),
        max_length=255,
        blank=True
    )

    image = ResizedImageField(
        quality=100,
        upload_to=image_folder,
        null=False,
        blank=False
    )

    sort_order = SortOrderField(
        _("الترتيب"),
        validators=[
            MinValueValidator(0)
        ]
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True)

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('اللافتات')
        verbose_name_plural = _('اللافتات')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return self.image.name


class Availability(models.Model):
    """
    This table is used to store the availability of employee
    """

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='availability'
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='availability',
        null=True

    )

    date = models.DateField(
        _('تاريخ يوم الدوام'),
    )

    start = models.TimeField(
        _('وقت بداية الدوام'),
    )

    end = models.TimeField(
        _('وقت نهاية الدوام'),
    )

    description = models.TextField(
        _('وصف الدوام'),
        null=True,
        blank=True
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    objects = managers.AvailabilityManager()

    class Meta:
        ordering = ['-date', 'start', 'end']
        verbose_name = _('تفاصيل الدوام')
        verbose_name_plural = _('تفاصيل الدوام')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.employee.__str__()}'

    @property
    def from_time(self):
        """

        @return: 
        """""
        return shortcut.time2delta(self.start)

    @property
    def to_time(self):
        """

        @return: 
        """""
        return shortcut.time2delta(self.end)


class BankAccount(models.Model):
    """
    This class is used store bank account in database.
    """

    vendor = models.ForeignKey(
        Vendor,
        related_name='bank_account',
        on_delete=models.CASCADE
    )

    account_name = models.CharField(
        _('إسم حساب البنك'),
        max_length=255,
    )

    account_number = models.CharField(
        _('رقم الحساب البنكي'),
        max_length=255,
    )

    branch_code = models.CharField(
        _('رقم الفرع'),
        max_length=255,
    )

    iban_number = models.CharField(
        _('رقم الحساب المصرفي الدولي آيبان'),
        max_length=255,
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    objects = managers.BankAccountManager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('الحساب البنكي')
        verbose_name_plural = _('الحساب البنكي')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.account_name}'


class WithdrawRequest(models.Model):
    """
    This class is used store withdraw request in database.
    """

    class StatusChoices(models.TextChoices):
        """
        This class contains availability such as open or close
        """
        PENDING = 'pending', _('في الانتظار')
        CANCEL = 'cancel', _('إلغاء الطلب')
        ARRIVAL = 'arrival', _('تم الدفع')

    vendor = models.ForeignKey(
        Vendor,
        related_name='withdraw_request',
        on_delete=models.CASCADE
    )

    bank = models.ForeignKey(
        BankAccount,
        related_name='withdraw_request',
        on_delete=models.CASCADE
    )

    amount = models.FloatField(
        _('المبلغ المطلوب'),
    )

    invoices = GenericRelation(
        admin_model.File,
        related_query_name='invoices'
    )

    notes = models.TextField(
        _('ملاحظات'),
        null=True,
        blank=True
    )

    status = models.CharField(
        _('حالة الطلب'),
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    objects = managers.WithdrawRequestManager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('طلبات العملاء')
        verbose_name_plural = _('طلبات العملاء')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.vendor.__str__()}'

    @property
    def get_amount_display(self):
        """
        This methode is used ro return price
        @return: price.
        """
        return shortcut.get_intcomma_display(self.amount)
