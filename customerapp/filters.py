import django_filters
from django_filters import rest_framework as filters

from vendorapp import models as vendor_model
from . import models


class BannerFilter(filters.FilterSet):
    class Meta:
        model = vendor_model.Banner
        fields = {
            'vendors__slug': ['in'],
            'banner_type': ['exact'],
            'created_date': ['date__range'],
        }


class VendorFilter(filters.FilterSet):
    class Meta:
        model = vendor_model.Vendor
        fields = {
            'vendor_type': ['exact'],
            'place': ['exact'],
            'allowed': ['exact'],
            'city__slug': ['exact'],
            'street': ['exact'],
            'time_from': ['gte'],
            'time_to': ['lte'],
            'created_date': ['date__range'],
            'rate': ['range'],
            'tags__name': ['exact', 'in'],
        }


class ServiceFilter(filters.FilterSet):
    vendor = django_filters.CharFilter(field_name='sales__vendor__slug', lookup_expr='exact')

    class Meta:
        model = vendor_model.Service
        fields = {
            'type': ['exact'],
            'place': ['exact'],
            'tags__name': ['exact', 'in'],
            'created_date': ['date__range'],
            'price': ['range'],
        }


class EmployeeFilter(filters.FilterSet):
    class Meta:
        model = vendor_model.Employee
        fields = {
            'vendor__slug': ['exact'],
            'service': ['exact'],
        }


class AvailabilityFilter(filters.FilterSet):
    class Meta:
        model = vendor_model.Availability
        fields = {
            'date': ['exact', 'year', 'month', 'day'],
            'employee': ['exact'],
            'service': ['exact']
        }


class OrderFilter(filters.FilterSet):
    class Meta:
        model = models.Order
        fields = {
            'status': ['exact'],
            'vendor': ['exact'],
            'created_date': ['date__range'],
        }
