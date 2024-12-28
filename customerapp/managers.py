from django.conf import settings
from django.db import models
from django.db.models import Q
from django_softdelete.models import SoftDeleteManager, SoftDeleteQuerySet
from django.utils import timezone


class OrderManager(SoftDeleteManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def order_status(self, status, **filters):
        """
        this function is used to filter queryset using order status
        @param status: order status
        @param filters: another values using to filter
        @return QuerySet
        """

        return self.filter(status=status, **filters)

    def pending(self, **filters):
        """
        this function ir return pending Queryset
        """
        return self.order_status(status=self.model.OrderStatusChoices.PENDING, **filters)

    def approval(self, **filters):
        """
        this function ir return approval Queryset
        """
        return self.order_status(status=self.model.OrderStatusChoices.APPROVAL, **filters)

    def disapproval(self, **filters):
        """
        this function ir return disapproval Queryset
        """
        return self.order_status(status=self.model.OrderStatusChoices.DISAPPROVAL, **filters)

    def payment(self, **filters):
        """
        this function ir return processing Queryset
        """

        return self.order_status(status=self.model.OrderStatusChoices.PAYMENT, **filters)

    def completed(self, **filters):
        """
        this function ir return completed Queryset
        """
        return self.order_status(status=self.model.OrderStatusChoices.COMPLETED, **filters)

    def pending_or_approval(self, **filters):
        """
        this function ir return pending Queryset
        """
        status = Q(status=self.model.OrderStatusChoices.PENDING) | Q(status=self.model.OrderStatusChoices.APPROVAL)
        return self.filter(status, **filters)

    def all_customer_orders(self, customer, **filters):
        """
        This method is used return all orders for customer
        @param customer: custom customer
        @return: QuerySet
        """
        return self.filter(customer=customer, **filters)

    def all_vendor_orders(self, vendor, **filters):
        """
        This method is used return all orders for vendor
        @param vendor: vendor customer
        @return: QuerySet
        """
        return self.filter(vendor=vendor, **filters)


class WalletQuerySet(SoftDeleteQuerySet):
    """
    This class is used to queryset wallet model and add some
    function like deposit or withdraw
    """

    def deposit(self, amount, **filters):
        """
        this function is used for deposit money to wallet
        @param amount: the amount of money
        @param filters: the dict of values
        @return: Boolean
        """
        if amount <= 0:
            return False

        queryset = self.filter(**filters)

        for raw in queryset:
            raw.balance += amount
            raw.last_operation = timezone.now()
            raw.save()

        return True

    def withdraw(self, amount, **filters):
        """
        this function is used for withdraw money from wallet
        @param amount: the amount of withdraw
        @param filters: the dict of values
        @return: Boolean
        """
        if amount <= 0:
            return False

        queryset = self.filter(**filters)

        for raw in queryset:
            if not (raw.balance - amount < 0):
                raw.balance -= amount
                raw.last_operation = timezone.now()
                raw.save()
        return True


class WalletManager(SoftDeleteManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def get_queryset(self):
        return WalletQuerySet(self.model, self._db).filter(is_deleted=False)

    def wallet(self, customer, **filters):
        """
        This method is used for the filter of wallet by customer
        passed from the variable with the name customer
        @param customer:The value of customer
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.filter(customer=customer, **filters)


class WalletVerifiedManager(WalletManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, self._db).filter(is_deleted=False, is_active=True)


class InvoiceManager(SoftDeleteManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    FIELDS_REQUIRED = ['price', 'tax']

    def __create(self, order, offer=None):
        """
        this function is used to create invoice object
        @param order: the order instance
        @return: invoice instance
        """
        status = self.model.InvoiceStatusChoices.COMPLETED
        customer = order.customer.user.get_full_name()
        discount = getattr(offer, 'discount', 0)
        kwargs = {item: getattr(order, item) for item in self.FIELDS_REQUIRED}
        return self.create(
            order=order, offer=offer, vendor=order.vendor.name, status=status,
            customer=customer, discount=discount, **kwargs
        )

    def create_invoice(self, order, offer=None):
        """
        this function is used to create invoice object
        @param order: the order instance
        @param offer: the offer instance
        @return: invoice instance
        """
        from .models import InvoiceLineItem
        invoice = self.__create(order, offer)
        for order_item in order.order_item.all():
            InvoiceLineItem.objects.create_invoice_item(invoice, order_item)
        return invoice


class InvoiceItemManager(models.Manager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """
    FIELDS_REQUIRED = [
        'employee', 'price', 'discount', 'tax', 'date', 'start', 'end', 'quantity'
    ]

    def create_invoice_item(self, invoice, order_item):
        """
        this function is used to create invoice item object
        @param invoice: the invoice instance
        @param order_item: the order item instance
        @return: invoice item instance
        """
        service = order_item.sales.services.first().name
        kwargs = {item: getattr(order_item, item) for item in self.FIELDS_REQUIRED}
        return self.create(invoice=invoice, order_item=order_item, sales=service, **kwargs)


class PaymentProviderManager(models.Manager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def payment_done(self, payment, invoice):
        """
        This function is used to notify the order and the invoice that its value has been paid
        @param payment: Object of type paid
        @param invoice: These are used to pass the invoice value
        @return: void
        """
        payment.payments.create(invoice=invoice)
        invoice.order.payment()

    def create_payment(self, invoice, **kwargs):
        """
        This function is used to generate the payment
        @param invoice: These are used to pass the invoice value
        @param kwargs: This function is used to pass additional values
        @return: object of payment
        """
        pass


class WalletProviderManager(PaymentProviderManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def create_payment(self, invoice, **kwargs):
        """
        This function is used to generate the payment
        @param invoice: These are used to pass the invoice value
        @param kwargs: This function is used to pass additional values
        @return: object of payment
        """
        wallet = kwargs['wallet']
        amount = kwargs['amount']

        payment = self.create(wallet=wallet, amount=amount, currency=settings.DEFAULT_CURRENCY)
        self.payment_done(payment, invoice)
        return payment


class AlRajhiProviderManager(PaymentProviderManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def get_response_dict(self, **kwargs):
        """
        This function is used to return response elements
        @return: response elements
        """
        return dict(
            amount=kwargs['amt'],
            payment_id=kwargs['paymentid'],
            track_id=kwargs['trackid'],
            tran_id=kwargs['tranid'],
            trandata=kwargs['trandata'],
            result=kwargs['result'],
            currency=settings.DEFAULT_CURRENCY
        )

    def create_payment(self, invoice, **kwargs):
        """
        This function is used to generate the payment
        @param invoice: These are used to pass the invoice value
        @param kwargs: This function is used to pass additional values
        @return: object of payment
        """
        kwargs = self.get_response_dict(**kwargs)
        payment = self.create(**kwargs)
        self.payment_done(payment, invoice)
        return payment


class AlRajhiWithWalletProviderManager(AlRajhiProviderManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def discount_balance(self, wallet, amount, invoice):
        """
        This function is used to deduct the remaining balance from the wallet
        @return: wallet
        """

        if not wallet.is_withdraw_valid(amount):
            raise ValueError()

        wallet.withdraw(amount, wallet.customer.user)
        return wallet

    def get_response_dict(self, invoice, **kwargs):
        """
        This function is used to return response elements
        @return: response elements
        """
        response = super(AlRajhiWithWalletProviderManager, self).get_response_dict(**kwargs)
        alrajhi_amount = response['amount']
        wallet_amount = invoice.total - alrajhi_amount
        response.update({
            "amount": invoice.total,
            "alrajhi_amount": response['amount'],
            "wallet_amount": wallet_amount
        })
        return response

    def create_payment(self, wallet, invoice, **kwargs):
        """
        This function is used to generate the payment
        @param wallet: wallet object
        @param invoice: These are used to pass the invoice value
        @param kwargs: This function is used to pass additional values
        @return: object of payment
        """
        kwargs = self.get_response_dict(invoice, **kwargs)
        wallet_amount = kwargs['wallet_amount']
        wallet = self.discount_balance(wallet, wallet_amount, invoice)
        payment = self.create(wallet=wallet, **kwargs)
        self.payment_done(payment, invoice)
        return payment


class TamaraProviderManager(PaymentProviderManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def get_response_dict(self, **kwargs):
        """
        This function is used to return response elements
        @return: response elements
        """
        return dict(
            amount=kwargs['amt'],
            capture_id=kwargs['capture_id'],
            order_id=kwargs['order_id'],
            currency=settings.DEFAULT_CURRENCY
        )

    def create_payment(self, invoice, **kwargs):
        """
        This function is used to generate the payment
        @param invoice: These are used to pass the invoice value
        @param kwargs: This function is used to pass additional values
        @return: object of payment
        """
        kwargs = self.get_response_dict(**kwargs)
        payment = self.create(**kwargs)
        self.payment_done(payment, invoice)
        return payment
