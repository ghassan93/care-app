from django.conf import settings
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.views import INTERNAL_RESET_SESSION_TOKEN
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters, mixins
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from activatedapp.mixins import ActivateModelMixin
from adminapp import models as admin_model, serializers as admin_serializer
from adminapp.models import Policies
from utils import permissions, template
from . import serializers, forms, models
from .jwt_response import jwt_response_payload_handler
from .mixins import PasswordContextMixin
from .shortcut import get_user_by_b34

"""
 ============================================================== 
     Django View Application for display Pages in website
 ============================================================== 
"""

INTERNAL_RESET_SESSION_KEY = "_password_reset_key"

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('username', 'email', 'phonenumber', 'password', 'password1', 'password2')
)

USER_MODEL = get_user_model()


class LoginView(template.AnonymousTemplateView):
    """
    this LoginView view for return login page it's used in dashboard
    """
    title = _("تسجيل الدخول")
    template_name = 'care/authapp/auth-login.html'


login_view = LoginView.as_view()


class LogoutView(template.LoginTemplateView):
    """
    this LogoutView view for action logout page it's used in dashboard
    """

    next_page = settings.LOGOUT_REDIRECT_URL

    def dispatch(self, request, *args, **kwargs):
        """
        The dispatch method takes in the request and ultimately returns the response.
        Normally, it returns a response by calling (IE dispatching to)
        another method like get. Think of it as a middleman between requests and responses.
        """
        self.process_log_out(request)
        next_page = self.next_page
        if next_page:
            # Redirect to this page until the session has been cleared.
            return HttpResponseRedirect(next_page)
        return super().dispatch(request, *args, **kwargs)

    def process_log_out(self, request):
        """This function is used to log out of the system"""
        logout(request)

    def post(self, request, *args, **kwargs):
        """Logout may be done via POST."""
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        This function is used to log out of the system
        thrown get function
        """
        return HttpResponseRedirect(self.next_page)


logout_view = LogoutView.as_view()


class LogoutDoneView(template.AnonymousTemplateView):
    """
    this LogoutDoneView view for redirect to logout page it's
    used in dashboard
    """

    title = _("تسجيل الخروج")
    template_name = 'care/authapp/auth-logout-done.html'


logout_done_view = LogoutDoneView.as_view()


class PasswordRestView(template.AnonymousTemplateView):
    """
    this PasswordRestView view for action reset password it's
    used in dashboard
    """

    title = _("إستعادة كلمة المرور")
    template_name = 'care/authapp/auth-password-reset.html'


password_rest_view = PasswordRestView.as_view()


class PasswordRestDoneView(template.AnonymousTemplateView):
    """
    this PasswordRestDoneView view for redirect to reset password done  it's
    used in dashboard
    """

    title = _('إستعادة كلمة المرور')
    template_name = 'care/authapp/auth-password-reset-done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.session.get('email_was_sent', None)
        return context


password_rest_done_view = PasswordRestDoneView.as_view()


class PasswordResetKeyView(PasswordContextMixin, FormView):
    """
    this PasswordResetKeyView view for action reset password done  it's
    used in dashboard
    """

    form_class = forms.SetPasswordForm
    title = _('استعادة كلمة المرور')
    template_name = 'care/authapp/auth-password-reset-key.html'
    success_url = reverse_lazy('auth:reset_password_key_done_view')
    internal_reset_url_key = 'set-password'

    def dispatch(self, *args, **kwargs):
        """
        The dispatch method takes in the request and ultimately returns the response.
        Normally, it returns a response by calling (IE dispatching to)
        another method like get. Think of it as a middleman between requests and responses.
        """

        assert 'uidb36' in kwargs and 'code' in kwargs

        self.user = self.get_user(kwargs['uidb36'])

        if self.user is not None:
            self.code = kwargs['code']
            if self.code == self.internal_reset_url_key:
                self.code = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                otp_form = forms.BasePasswordCheckOTPForm(
                    data={'email': self.user.email, 'role': self.user.role, 'code': self.code}
                )
                if otp_form.is_valid():
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                otp_form = forms.BasePasswordCheckOTPForm(
                    data={'email': self.user.email, 'role': self.user.role, 'code': self.code}
                )
                if otp_form.is_valid():
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = self.code
                    redirect_url = self.request.path.replace(self.code, self.internal_reset_url_key)
                    return HttpResponseRedirect(redirect_url)

            return self.render_to_response(self.get_context_data())

    def get_user(self, uidb36):
        """
        This function fetches the user by passing uidb36
        @return: user
        """
        return get_user_by_b34(uidb36)

    def get_form_kwargs(self):
        """
        This function builds data in the form of a dictionary
        @return: kwargs
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        """
        This function checks the form data
        @return: boolean result
        """
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        This function builds data in the form of a dictionary
        @return: kwargs
        """
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
            context['user'] = self.user
            context['code'] = self.code
        else:
            context.update({
                'form': None,
                'title': _('فشلت عملية استعادة كلمة المرور'),
                'validlink': False,
            })
        return context


password_rest_key_view = PasswordResetKeyView.as_view()


class PasswordRestKeyDoneView(template.AnonymousTemplateView):
    """
    this PasswordRestKeyDoneView view for action reset password done  it's
    used in dashboard
    """
    title = _('تمت استعادة كلمة المرور بنجاح')
    template_name = 'care/authapp/auth-password-reset-key-done.html'


password_rest_key_done_view = PasswordRestKeyDoneView.as_view()


class RedirectAuthenticatedUserView(template.LoginTemplateView):
    """
    this RedirectAuthenticatedUserView view for action redirect it's
    used in dashboard
    """

    def dispatch(self, request, *args, **kwargs):
        """
        The dispatch method takes in the request and ultimately returns the response.
        Normally, it returns a response by calling (IE dispatching to)
        another method like get. Think of it as a middleman between requests and responses.
        """
        if self.request.user.is_authenticated:
            if request.user.is_admin:
                return redirect('admin:home_view')
            else:
                raise PermissionDenied()
        return redirect('auth:login_view')


redirect_authenticated_user_view = RedirectAuthenticatedUserView.as_view()


class PolicesView(View):
    """
    This class is used to return policies for system policies.
    this is return  HttpResponse for object of policies.
    """

    title = _('نظام كير')

    def get_object(self, slug):
        """
        This function is used to return policies slug
        @param slug: object slug
        @return: object
        """
        return get_object_or_404(Policies, slug=slug, is_active=True)

    def get(self, request, slug=None, *args, **kwargs):
        """
        This function is used to return the privacy policy via get the function
        @return: HttpResponse
        """
        instance = self.get_object(slug)
        html = getattr(instance, f'content_{request.LANGUAGE_CODE}')
        return HttpResponse(html)


policies_view = PolicesView.as_view()


def entry_bad_request(request, *args, **kwargs):
    """
    The HyperText Transfer Protocol (HTTP) 400 Bad Request response status code
    indicates that the server cannot or will not process the request due to
    something that is perceived to be a client error
    @return: 400 Bad Request
    """
    return render(request, 'care/error/pages-400.html')


def entry_forbidden(request, *args, **kwargs):
    """
    The HTTP 403 Forbidden response status code indicates that the server understands
    the request but refuses to authorize it.
    @return: HTTP 403 Forbidden
    """
    return render(request, 'care/error/pages-403.html')


def entry_not_found(request, *args, **kwargs):
    """
    In computer network communications, the HTTP 404, 404 not found, 404, 404 error, page not found or file
    not found error message is a hypertext transfer protocol standard response code,
    to indicate that the browser was able to communicate with a given server,
    but the server could not find what was requested.
    @return:  404 not found
    """
    return render(request, 'care/error/pages-404.html')


def entry_internal_server_error(request, *args, **kwargs):
    """
    The server has encountered a situation it does not know how to handle.
    @return:500 Internal Server Error
    """
    return render(request, 'care/error/pages-500.html')


"""
 ============================================================== 
     Django RESTfull API (application programming interface)
 ============================================================== 
"""


class RegisterViewSet(viewsets.GenericViewSet):
    """
    This class is used to deal with the Register model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (permissions.IsAdminOrAnonymous,)
    serializer_class = serializers.UserSerializer
    choices = USER_MODEL.RoleChoices

    def get_response(self, instance):
        """
        Returns the response data for both the login and refresh views.
        Override to return a custom response such as including the
        serialized representation of the User.
        @return: user payload
        """
        return jwt_response_payload_handler(instance)

    def register(self, request, role, serializer_class=None):
        """
        this function is the general function for create new user in the
        system.
        @param request: the HTTP Protocol from django
        @param role: the choices from User model like customer or vendor or admin
        @param serializer_class: the serializer for create custom user
        @return: object of user
        """
        serializer_class = serializer_class or self.get_serializer_class()
        serializer = serializer_class(context={'request': request, 'role': role}, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(self.get_response(instance), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def vendor(self, request):
        """
        this function is used to register a vendor user in the
        system.
        @param request: the HTTP Protocol from django
        @return: object of user
        """
        return self.register(request, self.choices.VENDOR, serializers.VendorSerializer)

    @action(detail=False, methods=['post'])
    def customer(self, request):
        """
        this function is used to register a customer user in the
        system.
        @param request: the HTTP Protocol from django
        @return: object of user
        """
        return self.register(request, self.choices.CUSTOMER)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdmin])
    def superuser(self, request):
        """
        this function is used to register a superuser user in the
        system.
        the user can register superuser is must have admin property.
        @param request: the HTTP Protocol from django
        @return: object of user
        """
        return self.register(request, self.choices.ADMIN)


class AuthenticationViewSet(viewsets.GenericViewSet):
    """
    This class is used to deal with the Authentication model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """
    serializer_class = serializers.LoginSerializer
    permission_classes = (permissions.IsAnonymous,)

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        """
        The dispatch method takes in the request and ultimately returns the response.
        Normally, it returns a response by calling (IE dispatching to)
        another method like get. Think of it as a middleman between requests and responses.
        """
        return super(AuthenticationViewSet, self).dispatch(*args, **kwargs)

    def get_response(self, instance):
        """
        Returns the response data for both the login and refresh views.
        Override to return a custom response such as including the
        serialized representation of the User.
        @return: user payload
        """
        return jwt_response_payload_handler(instance)

    @action(detail=False, methods=['post'])
    def login(self, request, *args, **kwargs):
        """
        This API is used to log in to the system by passing the username and password.
        """
        serializer = self.get_serializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(self.get_response(instance), status=status.HTTP_201_CREATED)


class PasswordViewSet(viewsets.GenericViewSet):
    """
    This class is used to deal with the Password model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """
    serializer_class = serializers.PasswordResetSerializer
    permission_classes = (permissions.IsAnonymous,)

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        """
        The dispatch method takes in the request and ultimately returns the response.
        Normally, it returns a response by calling (IE dispatching to)
        another method like get. Think of it as a middleman between requests and responses.
        """
        return super(PasswordViewSet, self).dispatch(*args, **kwargs)

    @action(detail=False, methods=['post'])
    def reset(self, request, *args, **kwargs):
        """
        This api uses password reset by passing the user's email with the user roll
        """
        serializer = self.get_serializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self.request.session['email_was_sent'] = user.email
        return Response({
            'detail': _('رائع! تم إرسال تعليمات استعادة كلمة المرور إلى بريدك الإلكتروني.'),
            'url': ''
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def set(self, request):
        """
        This api is used to change the password by passing a verification code with the new password
        """
        serializer = serializers.SetPasswordSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': _('تم استعادة كلمة المرور الخاصة بحسابك.')},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change(self, request):
        """
        This api is used to modify the password by passing the old password along with the new password
        """
        user = self.request.user
        serializer = serializers.PasswordChangeSerializer(context={'user': user}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'تم تعديل كلمة المرور بنجاح'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def verify_code(self, request):
        """
        This api is used to verify the code sent to the email
        """
        serializer = serializers.PasswordCheckOTPSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('رمز التحقق المدخل صحيح.')}, status=status.HTTP_201_CREATED)


class EmailViewSet(viewsets.GenericViewSet):
    """
    This class is used to deal with the Email model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """
    serializer_class = serializers.EmailChangeSerializer
    permission_classes = (permissions.IsAnonymous,)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change(self, request, slug=None):
        """
        This API is used to modify the email by passing the new email
        """
        instance = request.user
        serializer = self.get_serializer(context={'request': request, 'user': instance}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'تم تعديل البريد الإلكتروني بنجاح.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def resend_code(self, request, *args, **kwargs):
        """
        This API is used to resend the code to the email
        """
        serializer = serializers.ResenActivateEmailSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'detail': _('تم بنجاح إرسال رسالة لتفعيل البريد الإلكتروني.')}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def activate(self, request, *args, **kwargs):
        """
        This API is used to activate the email by passing the email and verification code
        """
        serializer = serializers.ActivateEmailSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'detail': _('تم تفعيل البريد الإلكتروني بنجاح.')}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def verify_code(self, request):
        """
        This api is used to verify the code sent to the email
        """
        serializer = serializers.EmailCheckOTPSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('رمز التحقق المدخل صحيح.')}, status=status.HTTP_201_CREATED)


class UserProfileViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    This class is used to deal with the User model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_object(self):
        """
        This function is used to return the value of a specified object by
        either the object number or the token associated with the object
        """
        return self.request.user

    def list(self, request, *args, **kwargs):
        """
        Returns the information of the specified object through the pass token
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Update the information of the specified object through the pass token
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        """
        This function used to delete user profile
        """
        serializer = serializers.UserDeletionSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['Delete'], detail=False, url_path='deletion-request')
    def deletion_request(self, request, *args, **kwargs):
        """
        This function used to delete user profile
        """
        instance = self.get_object()
        instance.deletion.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddressViewSet(viewsets.ModelViewSet, ActivateModelMixin):
    """
    This class is used to deal with the Address model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    serializer_class = serializers.AddressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        this function is used to return all queryset
        @return: queryset
        """
        user = self.request.user
        return models.Address.objects.all_address(user)

    def update(self, request, *args, **kwargs):
        """
        This function is used to update the data of objects
        that were returned through a specific filter.
        This function is called through the HTTP protocol via the update function.
        """
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This class is used to deal with the City model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = admin_model.City.activated.all()
    serializer_class = admin_serializer.CitySerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'code', 'country']
    lookup_field = 'slug'


class NotificationViewSet(viewsets.ReadOnlyModelViewSet, mixins.DestroyModelMixin):
    """
    This class is used to deal with the Notification model as it includes some HTTP
    functions such as GET, POST, UPDATE and DELETE functionality.
    """

    queryset = None
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.NotificationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['description']

    def get_queryset(self):
        """
        this function is used to return all queryset
        @return: queryset
        """
        return self.request.user.notifications.active()

    @action(detail=False, methods=['get'])
    def read(self, request):
        """
        This function is used to return all read notifications that have been sent
        to the user
        @return: queryset
        """
        notification = request.user.notifications.read()
        page = self.paginate_queryset(notification)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(notification, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        This function is used to return all unread notifications that have been sent
        to the user
        @return: queryset
        """
        notification = request.user.notifications.unread()

        page = self.paginate_queryset(notification)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(notification, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post', 'get'])
    def mark_all_as_read(self, request):
        """
        This function changes the status of all notifications to read notifications
        @return: status
        """
        request.user.notifications.mark_all_as_read()
        return Response({'status': _('تمت العملية بنجاح')})

    @action(detail=False, methods=['post', 'get'])
    def mark_all_as_delete(self, request):
        """
        This function changes the status of all notifications to delete notifications
        @return: status
        """
        request.user.notifications.mark_all_as_deleted()
        return Response({'status': _('تمت العملية بنجاح')})

    @action(detail=False, methods=['post', 'get'])
    def make_disallow_notification(self, request):
        """
        This function prevents notifications from being sent to the user
        @return: status
        """
        request.user.make_disallow_notification()
        return Response({'status': _('تمت العملية بنجاح')})

    @action(detail=False, methods=['post', 'get'])
    def make_allow_notification(self, request):
        """
        This function allows sending notifications to the user
        @return: status
        """
        request.user.make_allow_notification()
        return Response({'status': _('تمت العملية بنجاح')})

    @action(detail=False, methods=['post'])
    def add_expo_token(self, request):
        """
        This function adds the user's Expo Token to the database
        in order to send notifications to them
        @return: detail
        """
        serializer = serializers.ExpoPushTokenSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('تمت إضافة الرمز بنجاح')}, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        """
        This function is used to deal with the process of deleting data through the delete function
        that is sent via the HTTP protocol
        @param instance: instance of model
        """
        instance.deleted = True
        instance.save()
