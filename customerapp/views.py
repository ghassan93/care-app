from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import ugettext_lazy as _
from mptt.templatetags.mptt_tags import cache_tree_children
from rest_framework import viewsets, filters, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from utils import permissions, template
from vendorapp import models as vendor_model
from vendorapp.shortcut import create_range_date
from . import serializers, models
from .filters import VendorFilter, ServiceFilter, EmployeeFilter, AvailabilityFilter, BannerFilter, OrderFilter
from .mixins import RequiredFieldsMixins

"""
 ============================================================== 
     Django View Application for display Pages in website
 ============================================================== 
"""


class PaymentSuccessView(template.AnonymousTemplateView):
    """
    This class is used to return the html page if the payment process through
    the system is successful
    """

    template_name = 'care/payment/success.html'


payment_success_view = PaymentSuccessView.as_view()


class PaymentCancelView(template.AnonymousTemplateView):
    """
    This class is used to return the html page if the payment process through
    the system is canceled
    """

    template_name = 'care/payment/cancel.html'


payment_cancel_view = PaymentCancelView.as_view()


class PaymentErrorView(template.AnonymousTemplateView):
    """
    This class is used to return the html page if the payment process through
    the system is fails
    """

    template_name = 'care/payment/error.html'


payment_error_view = PaymentErrorView.as_view()

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

    queryset = vendor_model.Tag.activated.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (AllowAny,)
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

    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of vendor types
        """
        return Response(vendor_model.VendorTypeChoice.choices)


class PlaceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Place model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of place types
        """
        return Response(vendor_model.Vendor.PlaceChoices.choices)


class PersonAllowedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Person Allowed model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of person allowed types
        """
        return Response(vendor_model.Vendor.AllowedChoices.choices)


class VendorStatusViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Vendor Status model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of vendor status
        """
        return Response(vendor_model.Vendor.StatusChoices.choices)


class OrderStatusViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Order Status model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of order status
        """
        return Response(models.Order.OrderStatusChoices.choices)


class PaymentTypeChoicesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Payment Type model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of payment types
        """
        return Response(vendor_model.Vendor.PaymentTypeChoices.choices)


class ScheduleTypeChoicesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Schedule Type model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        """
        This function is used to return a list of schedule Types
        """
        return Response(vendor_model.Service.ScheduleTypeChoices.choices)


class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This class is used to deal with the Banner model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = vendor_model.Banner.activated.all()
    serializer_class = serializers.BannerSerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = BannerFilter
    search_fields = ['subject', 'body']


class VendorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This class is used to deal with the Vendor model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = vendor_model.Vendor.verified_objects.all()
    serializer_class = serializers.VendorSerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = VendorFilter
    search_fields = ['name', 'slug', 'city', 'street', 'location']
    lookup_field = 'slug'


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This class is used to deal with the Service model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = vendor_model.Service.verified_objects.all()
    serializer_class = serializers.ServiceSerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = ServiceFilter
    search_fields = ['name', 'slug']
    lookup_field = 'slug'

    @action(methods=['GET'], detail=True, permission_classes=[permissions.IsCustomer], url_path='comment-tree')
    def comment_tree(self, request, *args, **kwargs):
        """
        this function is used to return comment tree
        """
        service = self.get_object()
        queryset = vendor_model.Comment.activated.filter(services=service, level=0)
        tree = cache_tree_children(queryset)

        page = self.paginate_queryset(tree)
        if page is not None:
            serializer = serializers.CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.CommentSerializer(tree, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[permissions.IsCustomer])
    def comment(self, request, *args, **kwargs):
        """
        this function is used to post comment
        """
        service = self.get_object()
        context = {'request': request, 'comment_object': service}
        serializer = serializers.CommentSerializer(context=context, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(_('تم نشر التعليق بنجاح'), status=status.HTTP_201_CREATED)


class EmployeeViewSet(RequiredFieldsMixins, viewsets.ReadOnlyModelViewSet):
    """
    This class is used to deal with the Employee model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = vendor_model.Employee.verified_objects.all()
    serializer_class = serializers.EmployeeSerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = EmployeeFilter
    required_fields = ['vendor', 'service']
    search_fields = ['name']


class AvailabilityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Availability model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = vendor_model.Availability.objects.all()
    serializer_class = serializers.AvailabilitySerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = AvailabilityFilter
    search_fields = ['name']
    required_params = {'date', 'employee', 'service'}

    def list(self, request, *args, **kwargs):
        """
        This function is used to return the list of available availability
        for a service or employee
        """
        response = list()
        query_params = set(self.request.query_params.keys())
        if len(self.required_params & query_params) >= 2:
            queryset = self.filter_queryset(self.get_queryset())
            for instance in queryset:
                create_range_date(instance, response, check_reserve=True)
        return Response(self.get_serializer(response, many=True).data)


class OrderViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    """
    This class is used to deal with the Order model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    permission_classes = (permissions.IsCustomer,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = OrderFilter
    search_fields = ['notes']
    http_method_names = ['get', 'post']

    def get_queryset(self):
        """
        this function is used to return queryset for wallet
        @return: queryset
        """
        return models.Order.verified_objects.all_customer_orders(self.request.user.customer)

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        data = kwargs.get('data', None)
        if data and 'service' in data.keys():
            serializer_class = serializers.CreateOrderUnscheduleSerializer
        else:
            serializer_class = serializers.CreateOrderScheduleSerializer
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)


class OfferCodeViewSet(viewsets.GenericViewSet):
    """
    This class is used to deal with the Offer model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    serializer_class = serializers.OfferCodeSerializer
    permission_classes = (permissions.IsCustomer,)

    @action(methods=['POST'], detail=False)
    def verify(self, request, *args, **kwargs):
        """
        This function is used to verify the discount code data.
        It returns the discount details. If this discount is available,
        an error message is returned.
        """
        serializer = self.get_serializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)


class WalletViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the Wallet model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    serializer_class = serializers.WalletSerializer
    permission_classes = (permissions.IsCustomer,)

    def get_queryset(self):
        """
        this function is used to return queryset for wallet
        @return: queryset
        """

        return models.Wallet.verified_objects.wallet(self.request.user.customer)

    @action(methods=['POST'], detail=False)
    def pay(self, request, *args, **kwargs):
        """
        This function is used to pay through the wallet system,
        where the value of the order is deducted from the user's balance
        """
        serializer = serializers.WalletPaymentSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(_('تم دفع مبلع الطلب بشكل صحيح'))


class AlrajhiViewSet(viewsets.GenericViewSet):
    """
    This class is used to deal with the Alrajhi model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    serializer_class = serializers.AlrajhiPaymentSerializer
    permission_classes = (permissions.IsCustomer,)

    @action(methods=['POST'], detail=False)
    def get_page(self, request, *args, **kwargs):
        """
        This function is used to return the Al Rajhi payment page to the user
        """
        serializer = serializers.AlrajhiGetPageURLSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            {
                'page_id': instance.page_id,
                'page_url': instance.get_page_url()
            }
        )

    @action(methods=['POST'], detail=False, permission_classes=[])
    def success(self, request, *args, **kwargs):
        """
        This API is used by Al Rajhi system in the event
        of the success or failure of the payment process.
        This function checks for this and returns an HTML page to the user showing
        the success or failure of the transaction.
        """
        serializer = serializers.AlrajhiPaymentSerializer(context={'request': request}, data=request.data)

        if not serializer.is_valid():
            return redirect('customerapp:payment_error_view')

        serializer.save()
        return redirect('customerapp:payment_success_view')

    @action(methods=['POST'], detail=False, permission_classes=[])
    def error(self, request, *args, **kwargs):
        """
        This API is used by Al Rajhi system in the event
        of the success or failure of the payment process.
        This function checks for this and returns an HTML page to the user showing
        the success or failure of the transaction.
        """
        return Response(_('فشلت عملية دفع مبلغ الطلب'))


class TamaraViewSet(viewsets.GenericViewSet):
    """

    """

    permission_classes = (permissions.IsCustomer,)

    @action(methods=['POST'], detail=False)
    def get_page(self, request, *args, **kwargs):
        """
        This function is used to return the Tamara payment page to the user
        """

        serializer = serializers.TamaraGetPageURLSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            {
                'order_id': instance.order_id,
                'checkout_id': instance.checkout_id,
                'checkout_url': instance.checkout_url
            }
        )

    @action(methods=['GET'], detail=False, permission_classes=[])
    def success(self, request, *args, **kwargs):
        """
        """
        return redirect('customerapp:payment_success_view')

    @action(methods=['GET'], detail=False, permission_classes=[])
    def cancel(self, request, *args, **kwargs):
        """
        """
        return redirect('customerapp:payment_cancel_view')

    @action(methods=['GET'], detail=False, permission_classes=[])
    def error(self, request, *args, **kwargs):
        """
        """
        return redirect('customerapp:payment_error_view')

    @action(methods=['POST'], detail=False, permission_classes=[])
    def notification(self, request, *args, **kwargs):
        """
        """
        serializer = serializers.TamaraPaymentSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return redirect('customerapp:payment_success_view')
