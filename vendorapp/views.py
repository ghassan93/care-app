from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from mptt.templatetags.mptt_tags import cache_tree_children
from rest_framework import viewsets, filters, mixins, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from adminapp import models as admin_model
from customerapp.models import Order
from customerapp.signals import order_approval, order_disapproval
from utils import permissions
from utils.mixins import PhoneGenericRelationshipModelMixin, PictureGenericRelationshipModelMixin
from vendorapp import models, serializers
from vendorapp.filters import AvailabilityFilter, OrderFilter, CommentFilter
from vendorapp.shortcut import create_range_date

"""
 ============================================================== 
     Django RESTfull API (application programming interface)
 ============================================================== 
"""


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This class is used to deal with the Tags model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = models.Tag.activated.all()
    serializer_class = serializers.TagSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['tag_type', 'slug']
    search_fields = ['name']
    lookup_field = 'slug'
    paginator = None


class VendorTypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Vendor model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of vendor types
        """
        return Response(models.VendorTypeChoice.choices)


class PlaceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    A viewset that provides Place action
    """

    def list(self, request, *args, **kwargs):
        return Response(models.Vendor.PlaceChoices.choices)


class PersonAllowedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Place model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of place types
        """
        return Response(models.Vendor.AllowedChoices.choices)


class VendorStatusViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Vendor Status model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (permissions.IsVendor,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of vendor status
        """
        return Response(models.Vendor.StatusChoices.choices)


class PhoneTypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Phone Type model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (permissions.IsVendor,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of phone types
        """
        return Response(admin_model.Phone.PhoneTypeChoices.choices)


class PictureTypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Phone Type model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (permissions.IsVendor,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of picture types
        """
        return Response(admin_model.Picture.PictureTypeChoices.choices)


class HoursChoicesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Hours model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (permissions.IsVendor,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of hours choices
        """
        return Response(models.hours_choices())


class MinutesChoicesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Minutes model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (permissions.IsVendor,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of minutes choices
        """
        return Response(models.minutes_choices())


class PaymentTypeChoicesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Payment Type model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (permissions.IsVendor,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of payment types
        """
        return Response(models.Vendor.PaymentTypeChoices.choices)


class ScheduleTypeChoicesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Schedule Type model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (permissions.IsVendor,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of schedule Types
        """
        return Response(models.Service.ScheduleTypeChoices.choices)


class VendorViewSet(
    viewsets.GenericViewSet,
    PhoneGenericRelationshipModelMixin,
    PictureGenericRelationshipModelMixin
):
    """
    This class is used to deal with the Vendor model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    serializer_class = serializers.VendorSerializer
    permission_classes = (permissions.IsVendor,)

    def get_object(self):
        """
        This function is used to return the value of a specified object by
        either the object number or the token associated with the object
        """
        return self.request.user.vendor_user.vendor

    def list(self, request, *args, **kwargs):
        """
        This function is used to return vendor data based on the token
        passed through the header
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_vendor(self, request, *args, **kwargs):
        """
        This function is used to update the data of the vendor whose token
        has been passed through the HTTP header
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_phone(self, request, *args, **kwargs):
        """
        This function is used to add a new phone number to the vendor whose
        token has been passed through the HTTP header
        """
        return super(VendorViewSet, self).add_phone(request)

    @action(detail=False, methods=['post'])
    def add_picture(self, request, *args, **kwargs):
        """
        This function is used to add a new picture to the vendor whose
        token has been passed through the HTTP header
        """
        return super(VendorViewSet, self).add_picture(request)

    @action(detail=True, methods=['delete'])
    def delete_phone(self, request, pk, *args, **kwargs):
        """
        This function is used to delete a phone number from the vendor whose
        token has been passed through the HTTP header
        """

        return super(VendorViewSet, self).delete_phone(pk)

    @action(detail=True, methods=['delete'])
    def delete_picture(self, request, pk, *args, **kwargs):
        """
        This function is used to delete a picture from the vendor whose
        token has been passed through the HTTP header
        """
        return super(VendorViewSet, self).delete_picture(pk)


class ServiceViewSet(viewsets.ModelViewSet):
    """
    This class is used to deal with the Service model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    serializer_class = serializers.ServiceSerializer
    permission_classes = (permissions.IsVendor,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    parser_classes = (MultiPartParser, FormParser)
    filterset_fields = ['type', 'place', 'hour', 'minute', 'created_date']
    search_fields = ['name', 'slug', 'street', 'location']
    lookup_field = 'slug'

    def get_queryset(self):
        """
        this function is used to return queryset for wallet
        @return: queryset
        """
        return models.Service.sales_objects.all_sales(self.request.user.vendor_user.vendor)

    def update(self, request, *args, **kwargs):
        """
        This function is used to update the data of objects
        that were returned through a specific filter.
        This function is called through the HTTP protocol via the update function.
        """
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    @action(methods=['POST'], detail=True, permission_classes=[permissions.IsVendor])
    def comment(self, request, *args, **kwargs):
        """
        this function is used to post comment
        """
        service = self.get_object()
        serializer = serializers.CommentSerializer(context={'request': request, 'service': service}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(_('تم نشر التعليق بنجاح'), status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        """
        This function is used to delete the data of an object,
        as this function is called through the HTTP protocol via the delete function
        """

        if not instance.sales.first().order_item.all():
            return instance.hard_delete()

        return super(ServiceViewSet, self).perform_destroy(instance)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    This class is used to deal with the Employee model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    serializer_class = serializers.EmployeeSerializer
    permission_classes = (permissions.IsSelfCareVendor,)
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']

    def get_queryset(self):
        """
        this function is used to return queryset for wallet
        @return: queryset
        """
        return models.Employee.verified_objects.all_employees(self.request.user.vendor_user.vendor)

    def update(self, request, *args, **kwargs):
        """
        This function is used to update the data of objects
        that were returned through a specific filter.
        This function is called through the HTTP protocol via the update function.
        """
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        """
        This function is used to delete the data of an object,
        as this function is called through the HTTP protocol via the delete function
        """

        if not instance.order_item.all():
            return instance.hard_delete()

        return super(EmployeeViewSet, self).perform_destroy(instance)


class AvailabilityViewSet(viewsets.ModelViewSet):
    """
    This class is used to deal with the Availability model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    serializer_class = serializers.AvailabilitySerializer
    permission_classes = (permissions.IsVendor,)
    http_method_names = ['get', 'post', 'delete']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = AvailabilityFilter
    search_fields = ['name']
    required_params = {'date', 'employee', 'service'}

    def get_queryset(self):
        """
        this function is used to return queryset for wallet
        @return: queryset
        """
        return models.Availability.objects.vendor_availabilities(self.request.user.vendor_user.vendor)

    @action(methods=['get'], detail=False)
    def current_date(self, request, *args, **kwargs):
        """
        This function is used to return the list of available availability
        for a service or employee
        """
        response = list()
        query_params = set(self.request.query_params.keys())
        if len(self.required_params & query_params) >= 2:
            queryset = self.filter_queryset(self.get_queryset())
            for instance in queryset:
                create_range_date(instance, response)
        return Response(self.get_serializer(response, many=True).data)

    def create(self, request, *args, **kwargs):
        """
        This function is used to create an object.
        This function is called through the HTTP protocol via the Post function
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(_('تم إنشاء ألإتاحة بنجاح'), status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        """
        This function is used to delete the data of an object,
        as this function is called through the HTTP protocol via the delete function
        """

        if instance.reservation.filter(is_active=True):
            raise PermissionDenied(detail=_("لا يمكنك حذف هذا الكائن"))

        return super(AvailabilityViewSet, self).perform_destroy(instance)


class BankAccountViewSet(viewsets.ModelViewSet):
    """
    This class is used to deal with the Bank Account model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    serializer_class = serializers.BankAccountSerializer
    permission_classes = (permissions.IsVendor,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']

    def get_queryset(self):
        """
        this function is used to return queryset for wallet
        @return: queryset
        """
        return models.BankAccount.objects.all_banks(self.request.user.vendor_user.vendor)

    def perform_destroy(self, instance):
        """
        This function is used to delete the data of an object,
        as this function is called through the HTTP protocol via the delete function
        """

        if instance.withdraw_request.all():
            raise PermissionDenied(detail=_("لا يمكنك حذف هذا الكائن"))

        return super(BankAccountViewSet, self).perform_destroy(instance)


class WithdrawRequestViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    """
    This class is used to deal with the Withdraw Request model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    serializer_class = serializers.WithdrawRequestSerializer
    permission_classes = (permissions.IsVendor,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']

    def get_queryset(self):
        """
        this function is used to return queryset for wallet
        @return: queryset
        """
        return models.WithdrawRequest.objects.all_requests(self.request.user.vendor_user.vendor)


class OfferViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.ReadOnlyModelViewSet
):
    """
    This class is used to deal with the Offer model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    serializer_class = serializers.OfferSerializer
    permission_classes = (permissions.IsVendor,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']

    def get_queryset(self):
        """
        this function is used to return queryset for wallet
        @return: queryset
        """
        return models.Offer.offer_objects.vendors(self.request.user.vendor_user.vendor)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This class is used to deal with the Order model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    serializer_class = serializers.OrderSerializer
    permission_classes = (permissions.IsVendor,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = OrderFilter
    search_fields = ['notes']

    def get_queryset(self):
        """
        this function is used to return queryset for wallet
        @return: queryset
        """
        return Order.verified_objects.all_vendor_orders(self.request.user.vendor_user.vendor)

    @action(methods=['GET'], detail=True)
    def order_detail(self, request, *args, **kwargs):
        """
        This function is used to return the details of an order where the order ID
        is passed over HTTP
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def approval(self, request, *args, **kwargs):
        """
        This function is used to approval the order submitted by the customer to the vendor,
        where an email message is sent to the customer in case of acceptance or rejection
        """
        user = self.request.user
        queryset = Order.verified_objects.pending(vendor=user.vendor_user.vendor)
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        instance = get_object_or_404(queryset, **filter_kwargs)
        instance.approval()
        order_approval.send(sender=instance.__class__, order=instance)
        return Response(_('تم قبول الطلب بشكل صحيح'))

    @action(methods=['POST'], detail=True)
    def disapproval(self, request, *args, **kwargs):
        """
        This function is used to disapproval the order submitted by the customer to the vendor,
        where an email message is sent to the customer in case of acceptance or rejection
        """
        user = self.request.user
        queryset = Order.verified_objects.pending_or_approval(vendor=user.vendor_user.vendor)
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        instance = get_object_or_404(queryset, **filter_kwargs)
        instance.disapproval()
        order_disapproval.send(sender=instance.__class__, order=instance)
        return Response(_('تم رفض الطلب بشكل صحيح'))

    @action(methods=['POST'], detail=True)
    def completed(self, request, *args, **kwargs):
        """
        This function is used by the vendor if the order processing is completed
        """
        user = self.request.user
        query = Q(status=Order.OrderStatusChoices.PAYMENT) | Q(payment_type=Order.PaymentTypeChoices.VENDOR)
        queryset = Order.verified_objects.filter(query)
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        instance = get_object_or_404(queryset, **filter_kwargs)
        instance.completed()
        order_approval.send(sender=instance.__class__, order=instance)
        return Response(_('تم الانتهاء من الطلب بشكل صحيح'))


class CommentViewSet(viewsets.ModelViewSet):
    """
    This class is used to deal with the Service model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    serializer_class = serializers.CommentSerializer
    permission_classes = (permissions.IsVendor,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = CommentFilter

    def get_queryset(self):
        """
        this function is used to return queryset for wallet
        @return: queryset
        """
        vendor = self.request.user.vendor_user.vendor
        return models.Comment.activated.filter(services__sales__vendor=vendor)

    @action(methods=['GET'], detail=False, url_path='comment-tree')
    def comment_tree(self, request, *args, **kwargs):
        """
        this function is used to return comment tree
        """
        queryset = self.filter_queryset(self.get_queryset().filter(level=0))
        tree = cache_tree_children(queryset)

        page = self.paginate_queryset(tree)
        if page is not None:
            serializer = serializers.CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.CommentSerializer(tree, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def replay(self, request, *args, **kwargs):
        """
        This function is used by the replay the comment
        """
        comment = self.get_object()
        context = {'request': request, 'comment_object': comment.comment_object}
        serializer = serializers.CommentSerializer(context=context, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(parent=comment)
        return Response(_('تم نشر الرد بنجاح'), status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        This function is used to update the data of objects
        that were returned through a specific filter.
        This function is called through the HTTP protocol via the update function.
        """
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
