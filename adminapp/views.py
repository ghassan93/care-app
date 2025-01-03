from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from activatedapp.mixins import ActivateModelMixin
from authapp import serializers as auth_serializer
from customerapp.shortcut import get_qr_code, render_invoice_pdf
from utils import permissions, template
from utils.statistics import StatisticsData
from vendorapp import models as vendor_model
from customerapp import models as customer_model
from . import serializers, models
from .filtres import OrderFilter, UserFilter, VendorFilter, InvoiceFilter, OfferFilter, ServiceFilter, CityFilter, \
    PoliciesFilter, TagFilter, CommentFilter
    
from django.shortcuts import render
from customerapp.models import Customer
from .tasks import send_marketing_email_task
from project import settings
import os
from django.core.files.storage import default_storage

"""
 ============================================================== 
     Django View Application for display Pages in website
 ============================================================== 
"""


from django.shortcuts import render

def send_marketing_email_view(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        attachments = request.FILES.getlist('attachments')

        upload_folder = os.path.join(settings.MEDIA_ROOT, 'attachments')
        os.makedirs(upload_folder, exist_ok=True)

        attachment_data = []
        for attachment in attachments:
            file_path = os.path.join(upload_folder, attachment.name)
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in attachment.chunks():
                    destination.write(chunk)

            attachment_data.append({
                'name': attachment.name,
                'url': f"{settings.SITE_DOMAIN}{settings.MEDIA_URL}attachments/{attachment.name}",
                'content_type': attachment.content_type
            })
        print(attachment_data)

        # customers = Customer.objects.all()
        # for customer in customers:
        #     context = {
        #         'subject': subject,
        #         'message': message,
        #         'name': customer.name,
        #         'attachments': attachment_data
        #     }
        template_name = 'care/email/marketing_email.html'
        # recipient_list = ['garabeed@gmail.com'] if settings.TESTING_EMAIL_MODE else [customer.email]
        recipientname = 'ghassan'
        recipient_list = ['garabeed@gmail.com']
        context = {
            'subject': subject,
            'message': message,
            'name': recipientname,
            'attachments': attachment_data
        }
        print(context)
        send_marketing_email_task.delay(
            subject=subject,
            recipient_list=recipient_list,
            context=context,
            template_name=template_name
        )

        # عرض الصفحة بعد النجاح
        return render(request, 'care/email/sendSuccess.html')

    return render(request, 'care/email/send_email.html')



from vendorapp.models import Vendor
def test(request):
    vendors=Vendor.objects.all()
 
    for vendor in vendors:
        print(vendor)
    return render(request, 'care/email/marketing_email.html')



USER_MODEL = get_user_model()


class HomeView(template.AdminTemplateView):
    title = _("لوحة التحكم")
    template_name = 'care/adminapp/index.html'

    def get_context_data(self, **kwargs):
        """

        @param kwargs:
        @return:
        """
        context = super().get_context_data(**kwargs)
        context['vendors'] = vendor_model.Vendor.objects.all().order_by('-id')[:5]
        return context


home_view = HomeView.as_view()


class NotificationView(template.AdminTemplateView):
    title = _("الإشعارات")
    template_name = 'care/adminapp/notification/view.html'


notification_view = NotificationView.as_view()


class NotificationSettingsView(template.AdminTemplateView):
    title = _("الإشعارات")
    template_name = 'care/adminapp/notification/type.html'


notification_settings_view = NotificationSettingsView.as_view()


class NotificationMessagesView(template.AdminTemplateView):
    title = _("الإشعارات")
    template_name = 'care/adminapp/notification/message.html'

    def get_context_data(self, **kwargs):
        """

        @param kwargs:
        @return:
        """
        context = super().get_context_data(**kwargs)
        context['role'] = kwargs.get('role', '')
        return context


notification_messages_view = NotificationMessagesView.as_view()


class UserProfileView(template.AdminTemplateView):
    title = _("الصفحة الشخصية")
    template_name = 'care/adminapp/menu/profile.html'


user_profile_view = UserProfileView.as_view()


class CustomerView(template.AdminTemplateView):
    title = _("إدارة العملاء")
    template_name = 'care/adminapp/customer/view.html'


customer_view = CustomerView.as_view()


class CustomerCreateView(template.AdminTemplateView):
    title = _("إضافة عميل جديد")
    template_name = 'care/adminapp/customer/create.html'


customer_create_view = CustomerCreateView.as_view()


class CustomerUpdateView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("تعديل بينات العميل")
    template_name = 'care/adminapp/customer/update.html'
    model = USER_MODEL
    lookup_field = 'slug'


customer_update_view = CustomerUpdateView.as_view()


class WalletView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("تعديل بينات المحفظة")
    template_name = 'care/adminapp/customer/wallet.html'
    model = USER_MODEL
    lookup_field = 'slug'

    def get_object(self, **kwargs):
        """
        this function is used to return object
        @return:
        """
        filter_kwargs = {
            self.lookup_field: kwargs.get(self.lookup_field, None),
            'role': self.model.RoleChoices.CUSTOMER
        }
        instance = get_object_or_404(self.model, **filter_kwargs)
        return instance.customer.wallet


wallet_view = WalletView.as_view()


class VendorView(template.AdminTemplateView):
    title = _("إدارة البائعين")
    template_name = 'care/adminapp/vendor/view.html'


vendor_view = VendorView.as_view()


class VendorUpdateView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("إدارة البائعين")
    template_name = 'care/adminapp/vendor/update.html'
    model = vendor_model.Vendor
    lookup_field = 'slug'


vendor_update_view = VendorUpdateView.as_view()


class VendorDetailView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("إدارة البائعين")
    template_name = 'care/adminapp/vendor/detail.html'
    model = vendor_model.Vendor
    lookup_field = 'slug'


vendor_detail_view = VendorDetailView.as_view()


class VendorUserUpdateView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("تعديل بينات مستخدمي البائعين")
    template_name = 'care/adminapp/vendor/users/update.html'
    model = USER_MODEL
    lookup_field = 'slug'


vendor_user_update_view = VendorUserUpdateView.as_view()


class OrderView(template.AdminTemplateView):
    title = _("إدارة بيانات الطلبات")
    template_name = 'care/adminapp/order/view.html'


order_view = OrderView.as_view()


class OrderDetail(template.AdminTemplateView, template.TemplateDetailView):
    title = _("إدارة تفاصيل الطلبات")
    template_name = 'care/adminapp/order/detail.html'
    model = customer_model.Order
    lookup_field = 'pk'


order_detail_view = OrderDetail.as_view()


class InvoiceView(template.AdminTemplateView):
    title = _("إدارة بيانات الفواتير")
    template_name = 'care/adminapp/invoice/view.html'


invoice_view = InvoiceView.as_view()


class InvoiceDetail(template.AdminTemplateView, template.TemplateDetailView):
    title = _("إدارة تفاصيل الفاتورة")
    template_name = 'care/adminapp/invoice/detail.html'
    model = customer_model.Invoice
    lookup_field = 'pk'

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetail, self).get_context_data(**kwargs)
        instance = context['object']
        context['data'] = get_qr_code(instance)
        return context


invoice_detail_view = InvoiceDetail.as_view()


class GenerateInvoiceFile(template.AdminTemplateView, template.TemplateDetailView):
    title = _("إدارة تفاصيل الفاتورة")
    model = customer_model.Invoice
    lookup_field = 'pk'

    def get_context_data(self, **kwargs):
        """
        this function used to return file
        """
        invoice = self.get_object(**kwargs)
        pdf = render_invoice_pdf(invoice)
        kwargs.update({'pdf': pdf})
        return kwargs

    def get(self, request, *args, **kwargs):
        """
        this function used to get pdf file
        """
        context = self.get_context_data(**kwargs)
        pdf = context['pdf']
        return HttpResponse(pdf, content_type='application/pdf')


generate_invoice_file = GenerateInvoiceFile.as_view()


class ServiceView(template.AdminTemplateView):
    title = _("إدارة  بيانات الخدمات")
    template_name = 'care/adminapp/service/view.html'


service_view = ServiceView.as_view()


class ServiceUpdateView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("تعديل بينات الخدمة")
    template_name = 'care/adminapp/service/update.html'
    model = vendor_model.Service
    lookup_field = 'slug'


service_view_update_view = ServiceUpdateView.as_view()


class SettingsView(template.AdminTemplateView):
    title = _("اعدادت النظام")
    template_name = 'care/adminapp/menu/settings.html'


settings_view = SettingsView.as_view()


class ManagerView(template.AdminTemplateView):
    title = _("إدارة  بيانات المدراء")
    template_name = 'care/adminapp/manager/view.html'


manager_view = ManagerView.as_view()


class ManagerCreateView(template.AdminTemplateView):
    title = _("إضافة مدير جديد")
    template_name = 'care/adminapp/manager/create.html'


manager_create_view = ManagerCreateView.as_view()


class ManagerUpdateView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("تعديل بينات المدير")
    template_name = 'care/adminapp/manager/update.html'
    model = USER_MODEL
    lookup_field = 'slug'


manager_update_view = ManagerUpdateView.as_view()


class CityView(template.AdminTemplateView):
    title = _("إدارة  بيانات المدن")
    template_name = 'care/adminapp/city/view.html'


city_view = CityView.as_view()


class CityCreateView(template.AdminTemplateView):
    title = _("إضافة مدينة جديدة")
    template_name = 'care/adminapp/city/create.html'


city_create_view = CityCreateView.as_view()


class CityUpdateView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("تعديل بينات المدينة")
    template_name = 'care/adminapp/city/update.html'
    model = models.City
    lookup_field = 'slug'


city_update_view = CityUpdateView.as_view()


class PoliciesView(template.AdminTemplateView):
    title = _("إدارة  بيانات السياسات")
    template_name = 'care/adminapp/policies/view.html'


policies_view = PoliciesView.as_view()


class PoliciesCreateView(template.AdminTemplateView):
    title = _("إضافة سياسة جديدة")
    template_name = 'care/adminapp/policies/create.html'


policies_create_view = PoliciesCreateView.as_view()


class PoliciesUpdateView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("تعديل بينات السياسة")
    template_name = 'care/adminapp/policies/update.html'
    model = models.Policies
    lookup_field = 'slug'


policies_update_view = PoliciesUpdateView.as_view()


class TagView(template.AdminTemplateView):
    title = _("إدارة  بيانات الفئات")
    template_name = 'care/adminapp/tag/view.html'


tag_view = TagView.as_view()


class TagCreateView(template.AdminTemplateView):
    title = _("إضافة فئة جديدة")
    template_name = 'care/adminapp/tag/create.html'


tag_create_view = TagCreateView.as_view()


class TagUpdateView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("تعديل بينات الفئة")
    template_name = 'care/adminapp/tag/update.html'
    model = vendor_model.Tag
    lookup_field = 'slug'


tag_update_view = TagUpdateView.as_view()


class OfferView(template.AdminTemplateView):
    title = _("إدارة  بيانات الخصومات")
    template_name = 'care/adminapp/offer/view.html'


offer_view = OfferView.as_view()


class OfferCreateView(template.AdminTemplateView):
    title = _("إضافة الخصومات")
    template_name = 'care/adminapp/offer/create.html'


offer_create_view = OfferCreateView.as_view()


class OfferActivateView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("تنشيط الخصومات")
    template_name = 'care/adminapp/offer/activate.html'
    model = vendor_model.Offer
    lookup_field = 'pk'


activate_offer_code = OfferActivateView.as_view()


class WithdrawRequestView(template.AdminTemplateView):
    title = _("إدارة طلبات البائعين")
    template_name = 'care/adminapp/withdraw/view.html'


withdraw_request_view = WithdrawRequestView.as_view()


class WithdrawRequestUpdateView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("تعديل طلب البائع")
    template_name = 'care/adminapp/withdraw/update.html'
    model = vendor_model.WithdrawRequest
    lookup_field = 'pk'


withdraw_request_update_view = WithdrawRequestUpdateView.as_view()


class BannerView(template.AdminTemplateView):
    title = _("إدارة بيانات اللافتات")
    template_name = 'care/adminapp/banner/view.html'


banner_view = BannerView.as_view()


class BannerCreateView(template.AdminTemplateView):
    title = _("إضافة لافتة جديدة")
    template_name = 'care/adminapp/banner/create.html'

    def get_context_data(self, **kwargs):
        """
        this function is used to return context to template
        @param kwargs: dict of values
        @return: context
        """
        context = super(BannerCreateView, self).get_context_data(**kwargs)
        context['vendors'] = vendor_model.Vendor.verified_objects.all()
        return context


banner_create_view = BannerCreateView.as_view()


class BannerUpdateView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("تعديل بينات اللافتات")
    template_name = 'care/adminapp/banner/update.html'
    model = vendor_model.Banner
    lookup_field = 'pk'

    def get_context_data(self, **kwargs):
        """
        this function is used to return context to template
        @param kwargs: dict of values
        @return: context
        """
        context = super(BannerUpdateView, self).get_context_data(**kwargs)
        context['vendors'] = vendor_model.Vendor.verified_objects.all()
        return context


banner_update_view = BannerUpdateView.as_view()


class CommentView(template.AdminTemplateView):
    title = _("إدارة  بيانات التعليقات")
    template_name = 'care/adminapp/comment/view.html'


comment_view = CommentView.as_view()


class CommentUpdateView(template.AdminTemplateView, template.TemplateDetailView):
    title = _("تعديل بينات التعليقات")
    template_name = 'care/adminapp/comment/update.html'
    model = vendor_model.Comment
    lookup_field = 'pk'


comment_update_view = CommentUpdateView.as_view()

"""
 ============================================================== 
     Django RESTfull API (application programming interface)
 ============================================================== 
"""


class IndexViewSet(viewsets.GenericViewSet):
    """
    this class for handling statistics in dashboard
    """
    permission_classes = (permissions.IsAdmin,)

    @action(methods=['get'], detail=False)
    def statistics(self, request, *args, **kwargs):
        context = dict()
        context['vendors'] = USER_MODEL.user_objects.vendors().count()
        context['customers'] = USER_MODEL.user_objects.customers().count()
        context['services'] = vendor_model.Service.sales_objects.all().count()
        context['orders'] = customer_model.Order.verified_objects.all().count()
        return Response(data=context)

    @action(methods=['get'], detail=False)
    def statistics_vendor_chart(self, request, *args, **kwargs):
        statistics_data = StatisticsData(
            USER_MODEL.user_objects.vendors(),
            None,
            'date_joined'
        )
        data = statistics_data.get_statistics_data(prefix='vendor')
        return Response(data=data)

    @action(methods=['get'], detail=False)
    def statistics_customer_chart(self, request, *args, **kwargs):
        statistics_data = StatisticsData(
            USER_MODEL.user_objects.customers(),
            None,
            'date_joined'
        )
        data = statistics_data.get_statistics_data(prefix='customer')
        return Response(data=data)

    @action(methods=['get'], detail=False)
    def statistics_service_chart(self, request, *args, **kwargs):
        statistics_data = StatisticsData(
            vendor_model.Service.sales_objects.all(),
            None,
            'created_date'
        )
        data = statistics_data.get_statistics_data(prefix='service')
        return Response(data=data)


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    ActivateModelMixin,
    viewsets.GenericViewSet
):
    """
    A viewset that provides the User actions
    """

    queryset = USER_MODEL.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = UserFilter
    lookup_field = 'slug'

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    @action(methods=['post'], detail=True, )
    def change_password(self, request, slug=None):
        instance = self.get_object()
        serializer = serializers.PasswordChangeSerializer(context={'user': instance}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'تم تعديل كلمة المرور بنجاح.'}, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, )
    def change_username(self, request, slug=None):
        instance = self.get_object()
        serializer = auth_serializer.UsernameChangeSerializer(context={'user': instance}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'تم تعديل إسم المستخدم بنجاح.'}, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, )
    def change_email(self, request, slug=None):
        instance = self.get_object()
        context = {'request': request, 'user': instance}
        serializer = auth_serializer.EmailChangeSerializer(context=context, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'تم تعديل البريد الإلكتروني بنجاح.'}, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True)
    def restore(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.restore()
        return Response(_('تمت استعادة المستخدم بنجاح.'))

    @action(methods=['delete'], detail=True)
    def hard_delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.hard_delete()
        return Response(_('تم تأكيد حذف المستخدم بنجاح'))


class VendorViewSet(viewsets.ModelViewSet, ActivateModelMixin):
    """
     A viewset that provides the vendor actions
    """

    queryset = vendor_model.Vendor.objects.all().order_by('-id')
    serializer_class = serializers.VendorSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = VendorFilter
    lookup_field = 'slug'

    @action(methods=['get'], detail=True)
    def statistics(self, request, *args, **kwargs):
        context = dict()
        instance = self.get_object()
        context['users'] = instance.get_users().count()
        context['services'] = instance.get_sales().count()
        context['employees'] = instance.get_employees().count()
        context['orders'] = instance.get_orders().count()
        return Response(data=context)

    @action(methods=['get'], detail=True)
    def statistics_service_chart(self, request, *args, **kwargs):
        statistics_data = StatisticsData(self.get_object().get_sales(), None, 'created_date')
        data = statistics_data.get_statistics_data(prefix='service')
        return Response(data=data)

    def perform_destroy(self, instance):
        """
        this function used to delete vendor from system
        @return: none
        """
        [user.delete() for user in instance.get_users()]
        return super(VendorViewSet, self).perform_destroy(instance)

    @action(methods=['post'], detail=True)
    def restore(self, request, *args, **kwargs):
        instance = self.get_object()
        [user.restore() for user in USER_MODEL.objects.filter(vendor_user__vendor=instance)]
        instance.restore()
        return Response(_('تمت استعادة العميل بنجاح.'))

    @action(methods=['delete'], detail=True)
    def hard_delete(self, request, *args, **kwargs):
        instance = self.get_object()
        [user.hard_delete() for user in USER_MODEL.objects.filter(vendor_user__vendor=instance)]
        instance.hard_delete()
        return Response(_('تم تأكيد حذف العميل بنجاح'))


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    A viewset that provides the Order actions
    """
    queryset = customer_model.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = OrderFilter


class InvoiceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    A viewset that provides the Invoice actions
    """
    queryset = customer_model.Invoice.verified_objects.all()
    serializer_class = serializers.InvoiceSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = InvoiceFilter


class OfferViewSet(viewsets.ModelViewSet, ActivateModelMixin):
    """
    A viewset that provides the Offer actions
    """
    queryset = vendor_model.Offer.objects.all()
    serializer_class = serializers.OfferSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = OfferFilter
    http_method_names = ['get', 'post', 'delete']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            context={'request': request},
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['post'], detail=True)
    def activate_code(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.ActiveOfferSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(_('تم تفعيل الكود بنجاح'))

    @action(methods=['post'], detail=True)
    def restore(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.restore()
        return Response(_('تمت استعادة الخصم بنجاح.'))

    @action(methods=['delete'], detail=True)
    def hard_delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.hard_delete()
        return Response(_('تم تأكيد حذف الخصم بنجاح'))


class ServiceViewSet(viewsets.ModelViewSet, ActivateModelMixin):
    """
    A viewset that provides the Services actions
    """
    queryset = vendor_model.Service.sales_objects.all()
    serializer_class = serializers.ServiceSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = ServiceFilter
    lookup_field = 'slug'


class WithdrawRequestViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the Withdraw Request actions
    """
    queryset = vendor_model.WithdrawRequest.objects.all()
    serializer_class = serializers.WithdrawRequestSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    http_method_names = ['get', 'put', 'delete']
    search_fields = ['vendor__name', 'bank__account_name', 'bank__account_number', 'amount']

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class CityViewSet(viewsets.ModelViewSet, ActivateModelMixin):
    """
    A viewset that provides the City actions
    """
    queryset = models.City.objects.all()
    serializer_class = serializers.CitySerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = CityFilter
    lookup_field = 'slug'

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class PoliciesViewSet(viewsets.ModelViewSet, ActivateModelMixin):
    """
    A viewset that provides the Policies actions
    """
    queryset = models.Policies.objects.all()
    serializer_class = serializers.PoliciesSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = PoliciesFilter
    lookup_field = 'slug'

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class TgaViewSet(viewsets.ModelViewSet, ActivateModelMixin):
    """
    A viewset that provides the Tags actions
    """
    queryset = vendor_model.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = TagFilter
    lookup_field = 'slug'

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class BannerViewSet(viewsets.ModelViewSet, ActivateModelMixin):
    """
    A viewset that provides the Banner actions
    """
    queryset = vendor_model.Banner.objects.all()
    serializer_class = serializers.BannerSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['subject', 'body']

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class WalletViewSet(viewsets.ReadOnlyModelViewSet, ActivateModelMixin):
    """
    A viewset that provides the Wallet actions
    """
    queryset = customer_model.Wallet.objects.all()
    serializer_class = serializers.WalletSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'balance', 'customer__user__first_name',
        'customer__user__last_name', 'customer__user__email'
    ]

    @action(methods=['post'], detail=True)
    def deposit(self, request, *args, **kwargs):
        wallet = self.get_object()
        serializer = serializers.DepositSerializer(
            context={'request': request},
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(wallet=wallet)
        return Response(_('تم إيداع المبلغ بنجاح'))

    @action(methods=['post'], detail=True)
    def withdraw(self, request, *args, **kwargs):
        wallet = self.get_object()
        serializer = serializers.WithdrawSerializer(
            context={'request': request},
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(wallet=wallet)
        return Response(_('تم سحب المبلغ بنجاح'))


class CommentViewSet(viewsets.ModelViewSet, ActivateModelMixin):
    """
     A viewset that provides the comment actions
    """

    queryset = vendor_model.Comment.objects.all().order_by('-id')
    serializer_class = serializers.CommentSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = CommentFilter


class NotificationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    A viewset that provides the Notifications actions
    """
    queryset = None
    serializer_class = serializers.NotificationSerializer
    permission_classes = (permissions.IsAdmin,)
