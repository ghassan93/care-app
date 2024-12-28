from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django_random_id_model import RandomIDModel
from django.utils.translation import ugettext_lazy as _
from django_softdelete.models import SoftDeleteModel

from activatedapp.models import ActivatedModel
from authapp.models import Address
from customerapp import managers
from vendorapp import shortcut as vendor_shortcut
from vendorapp.models import Vendor, Sales, Employee, Availability, Offer, PriceBase, PriceMethodsBase

from . import shortcut


class Customer(models.Model):
    """
    This table is used to connect the user of a customer type with this table to facilitate
    the customer management process
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('المستخدم'),
        on_delete=models.CASCADE,
        related_name='customer'
    )
    @property
    def name(self):
        """
        Returns the full name of the user.
        """
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def email(self):
        """
        Returns the email of the user.
        """
        return self.user.email

    class Meta:
        ordering = ['-id']
        verbose_name = _('العميل')
        verbose_name_plural = _('العملاء')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return self.user.__str__()

    def get_orders(self):
        """
        this function is used to return all orders for customer
        @return: Queryset
        """
        return Order.verified_objects.all_customer_orders(self)


class Order(SoftDeleteModel, RandomIDModel, PriceMethodsBase):
    """
    This model is used to allow customers the process of booking a service within the CARE system by
    storing the customer number and the seller number with other information
    """

    class OrderStatusChoices(models.TextChoices):
        """
        This class contains availability such as open or close
        """
        PENDING = 'pending', _('في الانتظار')
        APPROVAL = 'approval', _('تم قبول الطلب')
        DISAPPROVAL = 'disapproval', _('تم رفض الطلب')
        PAYMENT = 'payment', _('تم الدفع')
        COMPLETED = 'completed', _('اكتمال المعالجة')

    class PaymentTypeChoices(models.TextChoices):
        """
        This class contains availability such as open or close
        """
        SYSTEM = 'system', _('الدفع من خلال النظام')
        VENDOR = 'vendor', _('الدفع من خلال البائع')

    customer = models.ForeignKey(
        Customer,
        related_name='orders',
        on_delete=models.CASCADE
    )

    vendor = models.ForeignKey(
        Vendor,
        related_name='orders',
        on_delete=models.CASCADE
    )

    status = models.CharField(
        _('حالة الطلب'),
        max_length=20,
        choices=OrderStatusChoices.choices,
        default=OrderStatusChoices.PENDING
    )

    payment_type = models.CharField(
        _('نوع الدفع'),
        max_length=20,
        choices=PaymentTypeChoices.choices,
        default=PaymentTypeChoices.SYSTEM
    )

    notes = models.TextField(
        _('ملاحظات'),
        null=True,
        blank=True
    )

    created_date = models.DateTimeField(
        _('تاريخ إرسال الطلب'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل على الطلب'),
        auto_now=True
    )

    verified_objects = managers.OrderManager()

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('الطلب')
        verbose_name_plural = _('الطلبات')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'Order no {self.id}'

    @property
    def tax(self):
        """
        This methode is used ro return tax
        @return: tax.
        """
        return settings.KSA_DEFAULT_TAX

    @property
    def discount(self):
        """
        This methode is used ro return discount
        @return: discount.
        """
        return 0

    @property
    def price(self):
        """
        This methode is used ro return price
        @return: tax.
        """
        total = 0

        for order_item in self.order_item.all():
            total += order_item.get_total_value

        return total

    @property
    def total(self):
        """
        This methode is used ro return total
        @return: tax.
        """
        return float(self.get_total_value)

    @property
    def is_payment(self):
        """
        this function return if order is payment True else False
        """
        return self.status == self.OrderStatusChoices.PAYMENT

    @property
    def is_approval(self):
        """
        this function return if order is approval True else False
        """
        return self.status == self.OrderStatusChoices.APPROVAL

    @property
    def is_disapproval(self):
        """
        this function return if order is disapproval True else False
        """
        return self.status == self.OrderStatusChoices.DISAPPROVAL

    @property
    def is_completed(self):
        """
        this function return if order is completed True else False
        """
        return self.status == self.OrderStatusChoices.COMPLETED

    def payment(self):
        """
        this function is used to change status tp payment
        """
        self.status = self.OrderStatusChoices.PAYMENT
        self.save()

    def approval(self):
        """
        This function is used to approval order
        """
        self.status = self.OrderStatusChoices.APPROVAL
        self.save()

    def disapproval(self):
        """
        This function is used to disapproval order
        """
        self.status = self.OrderStatusChoices.DISAPPROVAL
        self.save()

    def completed(self):
        """
        This function is used to completed order
        """
        self.status = self.OrderStatusChoices.COMPLETED
        self.save()


class OrderItem(PriceBase):
    """
    This model is used to allow customers the process of booking a service within the CARE system by storing
    the customer number and the seller number with other information
    """

    order = models.ForeignKey(
        Order,
        related_name='order_item',
        on_delete=models.CASCADE
    )

    sales = models.ForeignKey(
        Sales,
        related_name='order_item',
        on_delete=models.CASCADE
    )

    employee = models.ForeignKey(
        Employee,
        related_name='order_item',
        on_delete=models.SET_NULL,
        null=True
    )

    availability = models.ForeignKey(
        Availability,
        related_name='order_item',
        on_delete=models.SET_NULL,
        null=True
    )

    address = models.ForeignKey(
        Address,
        related_name='order_item',
        on_delete=models.SET_NULL,
        null=True
    )

    quantity = models.IntegerField(
        _('الكمية'),
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100000)
        ]
    )

    date = models.DateField(
        _('تاريخ يوم الحجز'),
        blank=True,
        null=True
    )

    start = models.TimeField(
        _('وقت بداية الحجز'),
        blank=True,
        null=True
    )

    end = models.TimeField(
        _('وقت نهاية الحجز'),
        blank=True,
        null=True
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
        verbose_name = _('عنصر الطلب')
        verbose_name_plural = _('عناصر الطلب')

    def __str__(self):
        return f'Order item no {self.id}'


class Reservation(ActivatedModel):
    """
    This table is used to store the reservation availability of employee
    """

    order_item = models.OneToOneField(
        OrderItem,
        related_name='reservation',
        on_delete=models.CASCADE
    )

    availability = models.ForeignKey(
        Availability,
        related_name='reservation',
        on_delete=models.CASCADE
    )

    date = models.DateField(
        _('تاريخ يوم الحجز'),
    )

    start = models.TimeField(
        _('وقت بداية الحجز'),
    )

    end = models.TimeField(
        _('وقت نهاية الحجز'),
    )

    class Meta:
        ordering = ['-date', 'start', 'end']
        verbose_name = _('تفاصيل الحجز')
        verbose_name_plural = _('تفاصيل الحجز')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.date} - {self.start} - {self.end}'


class Invoice(SoftDeleteModel, PriceBase):
    """
    This class used to save all order information
    """

    class InvoiceTypeChoices(models.TextChoices):
        """
        This class contains Invoice type
        """
        SALES = 'sales', _('فاتورة مبيعات')
        RETURNED = 'returned', _('فاتورة مرتجع')

    class InvoiceStatusChoices(models.TextChoices):
        """
        This class contains Invoice status
        """
        PENDING = 'pending', _('في انتظار دفع الفاتورة')
        COMPLETED = 'completed', _('تم دفع الفاتورة')
        CANCELED = 'canceled', _('تم إلغاء الفاتورة')

    annual_figure = models.IntegerField(
        _('الرقم السنوي'),
        null=False,
        validators=[
            MinValueValidator(1)
        ]
    )

    type = models.CharField(
        _('نوع الفاتورة'),
        max_length=20,
        choices=InvoiceTypeChoices.choices,
        default=InvoiceTypeChoices.SALES,
    )

    order = models.ForeignKey(
        Order,
        related_name='invoices',
        on_delete=models.SET_NULL,
        null=True
    )

    vendor = models.CharField(
        _('إسم البائع'),
        max_length=255,
    )

    customer = models.CharField(
        _('إسم المشتري'),
        max_length=255,
    )

    offer = models.ForeignKey(
        Offer,
        related_name='invoices',
        on_delete=models.SET_NULL,
        null=True
    )

    status = models.CharField(
        _('حالة الفاتورة'),
        max_length=20,
        choices=InvoiceStatusChoices.choices,
        default=InvoiceStatusChoices.PENDING
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    verified_objects = managers.InvoiceManager()

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('الفاتورة')
        verbose_name_plural = _('الفواتير')

    def save(self, *args, **kwargs):
        """If the user hasn't provided an ID, generate one at random and check
        that it has not been taken."""
        counter = 1
        filters = dict(created_date__year=vendor_shortcut.current_datetime().year)
        last_annual_figure = self.__class__.objects.filter(**filters)

        if last_annual_figure:
            counter += last_annual_figure.first().annual_figure

        self.annual_figure = counter

        super(Invoice, self).save(*args, **kwargs)

    def completed(self):
        """
        this function is used to change is_fee_paid to True
        """
        self.status = self.InvoiceStatusChoices.COMPLETED
        self.save()

    def canceled(self):
        """
        This function is used to approval order
        """
        self.status = self.InvoiceStatusChoices.CANCELED
        self.save()

    @property
    def get_discount_value(self):
        """
        This methode is used ro return discount
        @return: discount.
        """
        discount = vendor_shortcut.get_discount_value(self.get_price_value, getattr(self, 'discount'))
        return shortcut.get_correct_discount_value(discount)


class InvoiceLineItem(PriceBase):
    """
    This class used to save all order information
    """

    invoice = models.ForeignKey(
        Invoice,
        related_name='invoices_items',
        on_delete=models.CASCADE,
    )

    order_item = models.ForeignKey(
        OrderItem,
        related_name='invoices_items',
        on_delete=models.CASCADE,
    )

    sales = models.CharField(
        _('إسم المنتج'),
        max_length=255
    )

    employee = models.CharField(
        _('إسم الموظف'),
        max_length=255,
        blank=True,
        null=True
    )

    date = models.DateField(
        _('تاريخ بداية الحجز'),
        blank=True,
        null=True
    )

    start = models.TimeField(
        _('تاريخ نهاية الحجز'),
        blank=True,
        null=True
    )

    end = models.TimeField(
        _('تاريخ نهاية الحجز'),
        blank=True,
        null=True
    )

    quantity = models.IntegerField(
        _('الكمية'),
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100000)
        ]
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    objects = managers.InvoiceItemManager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('عنصر الفاتورة')
        verbose_name_plural = _('عناصر الفاتورة')


class Wallet(RandomIDModel, SoftDeleteModel, ActivatedModel):
    """
    this is class for save wallet Price
    """

    customer = models.OneToOneField(
        Customer,
        related_name='wallet',
        on_delete=models.CASCADE
    )

    balance = models.FloatField(
        _('المبلغ'),
        default=0.0,
        validators=[
            MinValueValidator(0.0)
        ]
    )

    last_operation = models.DateTimeField(
        _('تاريخ اخر عملية'),
        null=True
    )

    created_date = models.DateTimeField(
        _('تاريخ الإضافة'),
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        _('تاريخ التعديل'),
        auto_now=True
    )

    wallet_objects = managers.WalletManager()

    verified_objects = managers.WalletVerifiedManager()

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('المحفظة')
        verbose_name_plural = _('المحفظة')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.customer.__str__()}'

    @property
    def get_balance_display(self):
        """
        this function used to return balance display
        @return: balance
        """
        return vendor_shortcut.get_intcomma_display(self.balance)

    def is_deposit_valid(self, amount):
        """
        Check if the amount is valid for deposit
        @param amount: The total amount to be withdrawn
        @return:Boolean
        """

        if isinstance(amount, str):
            amount = float(amount)

        return amount > 0

    def is_withdraw_valid(self, amount):
        """
        This function checks the amount to be withdrawn from the wallet
        @param amount: The total amount to be withdrawn
        @return:Boolean
        """

        if isinstance(amount, str):
            amount = float(amount)

        return amount > 0 and self.balance - amount >= 0

    def deposit(self, amount, user):
        """
        this function is used for deposit money to wallet
        @param amount: the amount of money
        @param user: the object this creates this action
        @return: Boolean
        """

        if isinstance(amount, str):
            amount = float(amount)

        if not self.is_deposit_valid(amount):
            return False

        self.balance += amount
        self.last_operation = timezone.now()
        self.save()
        self.transaction(WalletTransaction.TransactionTypeChoices.DEPOSIT, amount, user)
        return True

    def withdraw(self, amount, user):
        """
        this function is used for withdraw money from wallet
        @param amount: the amount of withdraw
        @param user: the object this creates this action
        @return: Boolean
        """

        if isinstance(amount, str):
            amount = float(amount)

        if not self.is_withdraw_valid(amount):
            return False

        self.balance -= amount
        self.last_operation = timezone.now()
        self.save()
        self.transaction(WalletTransaction.TransactionTypeChoices.WITHDRAWAL, amount, user)
        return True

    def transaction(self, tran_type, amount, user):
        """
        this function is used to create wallet transaction
        @param tran_type: the type of transaction
        @param amount: the amount of money
        @param user: the object create this action
        @return:
        """
        return WalletTransaction.objects.create(wallet=self, type=tran_type, amount=amount, user=user)


class WalletTransaction(SoftDeleteModel):
    """
    this is class for save wallet Price
    """

    class TransactionTypeChoices(models.TextChoices):
        """
        This class contains Order types
        """
        WITHDRAWAL = 'withdrawal', _('سحب')
        DEPOSIT = 'deposit', _('إيداع')

    wallet = models.ForeignKey(
        Wallet,
        related_name='wallet_transaction',
        on_delete=models.CASCADE
    )

    amount = models.FloatField(
        _('الكمية'),
        default=0.0,
        validators=[
            MinValueValidator(0.0)
        ]
    )

    type = models.CharField(
        _('نوع العملية'),
        max_length=10,
        choices=TransactionTypeChoices.choices,
    )

    notes = models.TextField(
        _('ملاحظات'),
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('المستخدم'),
        on_delete=models.SET_NULL,
        related_name='wallet_transaction',
        null=True
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
        verbose_name = _('المحفظة')
        verbose_name_plural = _('المحفظة')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.get_type_display()} - {self.amount}'


class AlRajhiPaymentPageURL(ActivatedModel):
    """
    This class used to save AlRajhi Payment Page URL
    """

    class PaymentPageModeChoices(models.TextChoices):
        """
        This class contains Payment Page Mode
        """
        PRODUCTION = 'production', _('مرحلة النشر')
        DEVELOPMENT = 'development', _('مرحلة التطوير')

    order = models.ForeignKey(
        Order,
        related_name='alrajhi_payment_page_url',
        on_delete=models.CASCADE
    )

    offer = models.ForeignKey(
        Offer,
        related_name='alrajhi_payment_page_url',
        on_delete=models.SET_NULL,
        null=True
    )

    customer = models.ForeignKey(
        Customer,
        related_name='alrajhi_payment_page_url',
        on_delete=models.CASCADE
    )

    amount = models.FloatField(
        _('قيمة المبلغ المدفوع'),
        default=0.0
    )

    pay_via_wallet = models.BooleanField(
        _('إكمال الدفع عبر المحفظة'),
        default=False
    )

    mode = models.CharField(
        _('نوع العملية'),
        max_length=20,
        choices=PaymentPageModeChoices.choices,
    )

    page_id = models.CharField(
        _('رقم عملية الدفع'),
        max_length=255,
        unique=True,
        editable=False,
        error_messages={'unique': _('رقم عملية الدفع موجد مسبقاً.')},
    )

    track_id = models.CharField(
        _('رقم تتبع الدفع'),
        max_length=255,
        unique=True,
        editable=False,
        error_messages={'unique': _('رقم عملية الدفع موجد مسبقاً.')},
    )

    page_url = models.URLField(
        _('رابط عملية الدفع'),
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
        verbose_name = _('صفحة الدفع للراجحي')
        verbose_name_plural = _('صفحة الدفع للراجحي')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.page_id}'

    def get_page_url(self):
        """
        this function used to get page url
        @return: page url
        """
        return f'{self.page_url}?PaymentID={self.page_id}'


class Payment(models.Model):
    """
    this class is used to store payment operation
    """

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )

    object_id = models.PositiveBigIntegerField()

    payment_object = GenericForeignKey()

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
        verbose_name = _('الدفع')
        verbose_name_plural = _('الدفع')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'Payment Object {self.pk}'


class PaymentProviderBase(RandomIDModel, SoftDeleteModel):
    """
    This class is used to link the payment process with the order
    """

    class PaymentTypeChoices(models.TextChoices):
        """
        This class contains Order types
        """
        PURCHASE = 'purchase', _('شراء')
        REFUND = 'refund', _('إعادة')

    payments = GenericRelation(
        Payment,
        related_query_name='payment_provider_base'
    )

    type = models.CharField(
        _('نوع العملية'),
        max_length=10,
        choices=PaymentTypeChoices.choices,
        default=PaymentTypeChoices.PURCHASE,
    )

    amount = models.FloatField(
        _('المبلغ'),
        validators=[
            MinValueValidator(0.0)
        ]
    )

    currency = models.CharField(
        _('العملة'),
        max_length=20,
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
        abstract = True

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.id}'


class WalletProvider(PaymentProviderBase):
    """
    This class is used to link the payment process with the order
    """

    payments = GenericRelation(
        Payment,
        related_query_name='wallet'
    )

    wallet = models.ForeignKey(
        Wallet,
        related_name='wallet_provider',
        on_delete=models.SET_NULL,
        null=True
    )

    objects = managers.WalletProviderManager()

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('المحفظة')
        verbose_name_plural = _('المحفظة')


class AlRajhiBase(PaymentProviderBase):
    """
    This class is used to link the payment process with the order
    """

    payments = GenericRelation(
        Payment,
        related_query_name='alrajhi'
    )

    track_id = models.CharField(
        _('رقم تتبع الدفع'),
        max_length=255,
        editable=False
    )

    tran_id = models.CharField(
        _('رقم تتبع الدفع'),
        max_length=255,
        editable=False
    )

    payment_id = models.CharField(
        _('رقم عملية الدفع'),
        max_length=255,
        unique=True,
        error_messages={'unique': _('رقم عملية الدفع موجد مسبقاً.')},
    )

    trandata = models.TextField(
        _('البيانات المرسلة'),
        null=False,
        blank=False,
    )

    result = models.CharField(
        _('الناتج'),
        max_length=100
    )

    class Meta:
        abstract = True
        ordering = ['-created_date']
        verbose_name = _('الراجحي')
        verbose_name_plural = _('الراجحي')


class AlRajhiProvider(AlRajhiBase):
    """
    This class is used to link the payment process with the order
    """

    objects = managers.AlRajhiProviderManager()

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('الراجحي')
        verbose_name_plural = _('الراجحي')


class AlRajhiWithWalletProvider(AlRajhiBase):
    """
    This class is used to link the payment process with the order
    """

    payments = GenericRelation(
        Payment,
        related_query_name='alrajhi_with_wallet'
    )

    wallet = models.ForeignKey(
        Wallet,
        related_name='alrajhi_with_wallet',
        on_delete=models.SET_NULL,
        null=True
    )

    alrajhi_amount = models.FloatField(
        _('المبلغ من الراجحي'),
        validators=[
            MinValueValidator(0.0)
        ]
    )

    wallet_amount = models.FloatField(
        _('المبلغ من المحفظة'),
        validators=[
            MinValueValidator(0.0)
        ]
    )

    objects = managers.AlRajhiWithWalletProviderManager()

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('الدفع عبر الراجحي والمحفظة')
        verbose_name_plural = _('الدفع عبر الراجحي والمحفظة')


class TamaraPaymentPageURL(ActivatedModel):
    """
    This class used to save Tamara Payment Page URL
    """

    order = models.ForeignKey(
        Order,
        related_name='tamara_payment_page_url',
        on_delete=models.CASCADE
    )

    offer = models.ForeignKey(
        Offer,
        related_name='tamara_payment_page_url',
        on_delete=models.SET_NULL,
        null=True
    )

    customer = models.ForeignKey(
        Customer,
        related_name='tamara_payment_page_url',
        on_delete=models.CASCADE
    )

    amount = models.FloatField(
        _('قيمة المبلغ المدفوع'),
        default=0.0
    )

    order_track_id = models.TextField(
        _('رقم الطلب'),
        editable=False
    )

    checkout_id = models.TextField(
        _('رقم عملية الدفع'),
        editable=False
    )

    checkout_url = models.TextField(
        _('رابط عملية الدفع'),
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
        verbose_name = _('صفحة الدفع لتمارا')
        verbose_name_plural = _('صفحة الدفع لتمارا')

    def __str__(self):
        """
        This method used to return string of object.
        @return: str
        """
        return f'{self.order_id} - {self.checkout_id}'


class TamaraProvider(PaymentProviderBase):
    """
    This class is used to link the payment process with the order
    """

    payments = GenericRelation(
        Payment,
        related_query_name='tamara'
    )

    capture_id = models.TextField(
        _('رقم تتبع الدفع'),
        editable=False
    )

    order_id = models.TextField(
        _('رقم معرف الطلب'),
        editable=False
    )

    objects = managers.TamaraProviderManager()

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('تمارا')
        verbose_name_plural = _('تمارا')
