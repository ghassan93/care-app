import django_filters
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from customerapp.models import Order, Invoice
from vendorapp.models import Vendor, Offer, Service, Tag, Comment

from .models import City, Policies

USER_MODEL = get_user_model()


class UserFilter(filters.FilterSet):
    """
    This class used to filter all users based some fields
    and return to viewset model.
    """

    gender = django_filters.CharFilter(
        field_name='profile__gender',
        lookup_expr='exact'
    )

    city = django_filters.CharFilter(
        field_name='profile__city__slug',
        lookup_expr='exact'
    )

    class Meta:
        model = USER_MODEL
        fields = {
            'role': ['exact'],
            'is_deleted': ['exact'],
            'is_active': ['exact'],
            'username': ['contains'],
            'phonenumber': ['contains'],
            'email': ['contains'],
            'first_name': ['contains'],
            'last_name': ['contains'],
            'date_joined': ['date__range'],
            'updated_date': ['date__range'],
            'last_login': ['date__range'],
        }


class VendorFilter(filters.FilterSet):
    """
    This class used to filter all users based some fields
    and return to viewset model.
    """

    city = django_filters.CharFilter(
        field_name='city__slug',
        lookup_expr='exact'
    )

    tags = django_filters.CharFilter(
        field_name='tags__name__in',
        lookup_expr='exact'
    )

    class Meta:
        model = Vendor
        fields = {
            'id': ['exact'],
            'is_deleted': ['exact'],
            'name': ['contains'],
            'cr_no': ['contains'],
            'vendor_type': ['exact'],
            'place': ['exact'],
            'city': ['exact'],
            'rate': ['exact'],
            'payment_type': ['exact'],
            'allowed': ['exact'],
            'created_date': ['date__range'],
            'updated_date': ['date__range'],
        }


class OrderFilter(filters.FilterSet):
    """
    This class used to filter all orders based some fields
    and return to viewset model.
    """

    customer = django_filters.BaseCSVFilter(
        field_name='customer__user',
        lookup_expr='in'
    )

    vendor = django_filters.BaseCSVFilter(
        field_name='vendor',
        lookup_expr='in'
    )

    class Meta:
        model = Order
        fields = {
            'id': ['contains'],
            'status': ['exact'],
            'payment_type': ['exact'],
            'created_date': ['date__range'],
            'updated_date': ['date__range'],
        }


class InvoiceFilter(filters.FilterSet):
    """
    This class used to filter all invoices based some fields
    and return to viewset model.
    """

    customer = django_filters.BaseCSVFilter(
        field_name='order__customer__user',
        lookup_expr='in'
    )

    vendor = django_filters.BaseCSVFilter(
        field_name='order__vendor',
        lookup_expr='in'
    )

    order = django_filters.CharFilter(
        field_name='order__id',
        lookup_expr='contains'
    )

    class Meta:
        model = Invoice
        fields = {
            'id': ['contains'],
            'annual_figure': ['contains'],
            'type': ['exact'],
            'status': ['exact'],
            'offer': ['isnull'],
            'created_date': ['date__range'],
            'updated_date': ['date__range'],
        }


class OfferFilter(filters.FilterSet):
    """
    This class used to filter all offers based some fields
    and return to viewset model.
    """

    vendor = django_filters.BaseCSVFilter(
        field_name='vendor',
        lookup_expr='in'
    )

    class Meta:
        model = Offer
        fields = {
            'code': ['contains'],
            'is_deleted': ['exact'],
            'type': ['exact'],
            'expire_date': ['exact'],
            'created_date': ['date__range'],
            'updated_date': ['date__range'],
        }


class ServiceFilter(filters.FilterSet):
    """
    This class used to filter all services based some fields
    and return to viewset model.
    """

    vendor = django_filters.BaseCSVFilter(
        field_name='sales__vendor',
        lookup_expr='in'
    )

    class Meta:
        model = Service
        fields = {
            'name': ['contains'],
            'type': ['exact'],
            'place': ['exact'],
            'schedule': ['exact'],
            'created_date': ['date__range'],
            'updated_date': ['date__range'],
        }


class CityFilter(filters.FilterSet):
    """
    This class used to filter all cities based some fields
    and return to viewset model.
    """

    class Meta:
        model = City
        fields = {
            'name': ['contains'],
            'code': ['contains'],
            'created_date': ['date__range'],
            'updated_date': ['date__range'],
        }


class PoliciesFilter(filters.FilterSet):
    """
    This class used to filter all policies based some fields
    and return to viewset model.
    """

    class Meta:
        model = Policies
        fields = {
            'title': ['contains'],
            'created_date': ['date__range'],
            'updated_date': ['date__range'],
        }


class TagFilter(filters.FilterSet):
    """
    This class used to filter all tags based some fields
    and return to viewset model.
    """

    class Meta:
        model = Tag
        fields = {
            'name': ['contains'],
            'tag_type': ['exact'],
            'created_date': ['date__range'],
            'updated_date': ['date__range'],
        }


class CommentFilter(filters.FilterSet):
    """
    This class used to filter all comment based some fields
    and return to viewset model.
    """

    customer = django_filters.BaseCSVFilter(
        field_name='user',
        lookup_expr='in'
    )

    vendor = django_filters.BaseCSVFilter(
        field_name='services__sales__vendor__id',
        lookup_expr='in'
    )

    class Meta:
        model = Comment
        fields = {
            'content': ['contains'],
            'rate': ['exact'],
            'created_date': ['date__range'],
            'updated_date': ['date__range'],
        }
