from django.db import models
from django.db.models import Q
from django_softdelete.models import SoftDeleteManager, SoftDeleteQuerySet

from vendorapp.shortcut import current_datetime


class VendorManager(SoftDeleteManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def type(self, vendor_type, **filters):
        """
        This method is used for the filter of vendor type based on the type of vendor
        passed from the variable with the name vendor_type
        @param vendor_type:The value of vendor_type
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.filter(vendor_type=vendor_type, **filters)

    def self_care_vendors(self, **filters):
        """
        This method is used return all self care vendors from vendor
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.type('self-care', **filters)

    def car_care_vendors(self, **filters):
        """
        This method is used return all car care vendors from vendor
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.type('car-care', **filters)


class VendorVerifiedManager(VendorManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, self._db).filter(is_deleted=False, is_active=True)


class SalesBaseManager(SoftDeleteManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def all_sales(self, vendor, **filters):
        """
        This method is used return all sales for vendor
        @param vendor: custom vendor
        @return: QuerySet
        """
        return self.filter(sales__vendor=vendor, **filters)

    def self_care_sales(self, vendor, **filters):
        """
        This method is used return all self_care sales for vendor
        @param vendor: custom vendor
        @return: QuerySet
        """
        return self.all_sales(vendor, vendor__vendor_type='self-care')

    def car_care_sales(self, vendor, **filters):
        """
        This method is used return all car_care sales for vendor
        @param vendor: custom vendor
        @return: QuerySet
        """
        return self.all_sales(vendor, vendor__vendor_type='car-care')


class SalesBaseVerifiedManager(SalesBaseManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, self._db).filter(is_deleted=False, is_active=True)


class EmployeeManager(SalesBaseManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, self._db).filter(is_deleted=False)

    def all_employees(self, vendor, **filters):
        """
        This method is used return all employees for vendor
        @param vendor: custom vendor
        @return: QuerySet
        """
        return self.filter(vendor=vendor, **filters)


class AvailabilityManager(models.Manager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def activated_availabilities(self, **filters):
        """
        This method is used return all activated availabilities
        @return: QuerySet
        """
        return self.filter(date__gte=current_datetime().date(), **filters)

    def vendor_availabilities(self, vendor, **filters):
        """
       This method is used return all availabilities for employee
       @param vendor: custom vendor
       @return: QuerySet
       """
        return self.filter(service__sales__vendor=vendor, **filters)

    def employee_availabilities(self, employee, **filters):
        """
        This method is used return all availabilities for employee
        @param employee: custom employee
        @return: QuerySet
        """
        return self.filter(employee=employee, **filters)

    def service_availabilities(self, service, **filters):
        """
        This method is used return all availabilities for service
        @param service: custom service
        @return: QuerySet
        """
        return self.filter(service=service, **filters)


class BankAccountManager(models.Manager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def all_banks(self, vendor, **filters):
        """
        This method is used for the filter of banks based on the vendor
        passed from the variable with the name vendor
        @param vendor:The value of vendor
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.filter(vendor=vendor, **filters)


class WithdrawRequestManager(models.Manager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def all_requests(self, vendor, **filters):
        """
        This method is used for the filter of withdraw requests based on the vendor
        passed from the variable with the name vendor
        @param vendor:The value of vendor
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.filter(vendor=vendor, **filters)

    def pends(self, **filters):
        """
        This method is used for the filter of withdraw requests based status pends
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.filter(status=self.model.StatusChoices.PENDING, **filters)

    def cancels(self, **filters):
        """
        This method is used for the filter of withdraw requests based status cancels
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.filter(status=self.model.StatusChoices.CANCEL, **filters)

    def arrivals(self, **filters):
        """
        This method is used for the filter of withdraw requests based status cancels
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.filter(status=self.model.StatusChoices.ARRIVAL, **filters)


class OfferManager(SoftDeleteManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def actives(self, *args, **filters):
        """
        This function returns whether the code passed in this function
        is enabled or not
        @return: QuerySet
        """
        qs = self.filter(
            is_active=True,
            expire_date__gte=current_datetime().date(),
            *args,
            **filters
        )
        [qs.exclude(pk=row.pk) for row in qs if not row.is_valid_counts]
        return qs

    def verified(self, code, user, vendor=None, **filters):
        """
        This function returns whether the code passed in this function
        is enabled or not
        @return: QuerySet
        """
        query = Q(
            ~Q(users__in=[user]) &
            Q(code=code) &
            Q(
                Q(vendor=vendor) |
                Q(type=self.model.OfferTypeChoices.ADMIN)
            )
        )

        queryset = self.filter(query)

        if not queryset:
            return None

        offer = queryset.first()

        if not offer.is_valid_counts:
            return None

        return offer

    def type(self, offer_type, **filters):
        """
        This method is used for the filter of offer based on the offer_type
        passed from the variable with the name offer_type
        @param offer_type:The value of offer_type
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.filter(type=offer_type, **filters)

    def admins(self, **filters):
        """
        this function return only offer from admin type
        @param filters: Dictionary of different fields
        @return: Queryset
        """
        return self.type('admin', **filters)

    def vendors(self, vendor, **filters):
        """
        this function return only offer from vendor type
        @param vendor:The value of vendor
        @param filters: Dictionary of different fields
        @return: Queryset
        """
        return self.type('vendor', vendor=vendor, **filters)

    def create_offer_vendor(self, **kwargs):
        """
        this function is used to create offer for vendor
        @param kwargs:Dictionary of different fields
        @return: object
        """

        if 'vendor' not in kwargs.keys():
            raise ValueError('you must pass vendor value')

        kwargs.update({
            'type': self.model.OfferTypeChoices.VENDOR,
            'is_active': True
        })

        return self.create(**kwargs)

    def create_offer_admin(self, **kwargs):
        """
        this function is used to create offer for admin
        @param kwargs:Dictionary of different fields
        @return: object
        """

        if 'vendor' in kwargs.keys():
            raise ValueError('you not must pass vendor value')

        kwargs.update({'type': self.model.OfferTypeChoices.ADMIN})

        return self.create(**kwargs)


class OfferVerifiedManager(OfferManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, self._db).filter(is_deleted=False, is_active=True)
