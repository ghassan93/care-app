import django_filters
from django_filters import rest_framework as filters

from customerapp.models import Order
from . import models
from .models import Comment


class AvailabilityFilter(filters.FilterSet):
    """
    This class used to filter Availability model using django_filters
    """

    class Meta:
        model = models.Availability
        fields = {
            'date': ['exact', 'year', 'month', 'day'],
            'employee': ['exact'],
            'service': ['exact']
        }


class OrderFilter(filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            'status': ['exact'],
            'created_date': ['date__range'],
        }


class CommentFilter(filters.FilterSet):
    """
    This class used to filter all comment based some fields
    and return to viewset model.
    """
    service = django_filters.CharFilter(
        field_name='services__slug',
        lookup_expr='exact'
    )

    class Meta:
        model = Comment
        fields = {
            'content': ['contains'],
            'rate': ['exact'],
            'created_date': ['date__range'],
            'updated_date': ['date__range'],
        }
