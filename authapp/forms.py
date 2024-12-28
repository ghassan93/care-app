from allauth.account.models import EmailAddress
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import SetPasswordForm as AuthSetPasswordForm
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import PasswordField, SignupForm, LoginForm, ChangePasswordForm, UserForm
from phonenumber_field.formfields import PhoneNumberField
from allauth.account.utils import perform_login

from utils.constants import Messages
from . import signals, shortcut, tokens

USER_MODEL = get_user_model()


class LoginForm(forms.Form):
    """
    This Form is used to allow the user to log into the system by requesting the following data:
    @ Username (either username or email - or phone number).
    @ Password (stored in the database).
    @ Remember me.
    """

    username = forms.CharField(
        label=_('إسم المستخدم'),
        max_length=settings.ACCOUNT_EMAIL_MAX_LENGTH,
        min_length=settings.ACCOUNT_USERNAME_MIN_LENGTH
    )

    password = PasswordField(
        label=_('كلمة المرور'),
        autocomplete='current-password',
        max_length=settings.ACCOUNT_PASSWORD_MAX_LENGTH,
        min_length=settings.ACCOUNT_PASSWORD_MIN_LENGTH
    )

    role = forms.ChoiceField(
        label=_('نوع المستخدم'),
        choices=USER_MODEL.RoleChoices.choices
    )

    remember = forms.BooleanField(label=_('تذكرني'), required=False)

    user = None

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(LoginForm, self).__init__(*args, **kwargs)

    def user_credentials(self):
        """
        Provides the credentials required to authenticate the user for
        login.
        """
        credentials = {
            'username': self.cleaned_data['username'],
            'password': self.cleaned_data['password'],
            'role': self.cleaned_data['role']
        }
        return credentials

    def clean_username(self):
        username = self.cleaned_data['username']
        return username.strip()

    def clean(self):
        super(LoginForm, self).clean()
        if self._errors:
            return
        credentials = self.user_credentials()
        user = authenticate(self.request, **credentials)
        if user:
            self.user = user
        else:
            raise forms.ValidationError(
                message=Messages.USERNAME_PASSWORD_MISMATCH['message'],
                code=Messages.USERNAME_PASSWORD_MISMATCH['code']
            )
        return self.cleaned_data

    def session_login(self):
        """
        this login for only user admin
        """
        res = perform_login(
            self.request,
            self.user,
            email_verification=settings.ACCOUNT_EMAIL_VERIFICATION,
            redirect_url=settings.LOGIN_REDIRECT_URL,
            email=self.user.email,
        )

        remember = self.cleaned_data['remember']

        if remember:
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        else:
            self.request.session.set_expiry(0)

    def login(self, **kwargs):
        """
        login users
        """
        if self.user.is_admin:
            self.session_login()

        return self.user


class BaseResetPassword(forms.Form):
    """
    This class uses the password recovery feature through e-mail
    """

    email = forms.EmailField(
        label=_("البريد الإلكتروني"),
        required=True,
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "placeholder": _("عنوان البريد الإلكتروني"),
                "autocomplete": "email",
            }
        ),
    )

    role = forms.ChoiceField(
        label=_('نوع المستخدم'),
        choices=USER_MODEL.RoleChoices.choices
    )

    user = None

    def clean(self):
        """

        @return: phonenumber
        """
        email = self.cleaned_data['email']
        role = self.cleaned_data['role']
        self.user = shortcut.filter_user_objects_by_kwargs(email=email, role=role)
        if not self.user:
            raise forms.ValidationError(
                message=Messages.EMAIL_NOT_FOUND['message'],
                code=Messages.EMAIL_NOT_FOUND['code']
            )

        return self.cleaned_data

    def save(self, **kwargs):
        """
        This save() method accepts an optional commit keyword argument,
        which accepts either True or False.
        If you call save() with commit=False,
        then it will return an object that hasn’t yet been saved to the database.
        @return:
        """
        return self.cleaned_data


class BasePasswordCheckOTPForm(BaseResetPassword):
    """
    This class uses to validate password recovery feature through e-mail
    """

    code = forms.CharField(
        label=_("رمز التحقق"),
        required=True,
        max_length=settings.ACCOUNT_CODE_MAX_LENGTH,
        min_length=settings.ACCOUNT_CODE_MIN_LENGTH
    )

    def clean(self):
        cleaned_data = super(BasePasswordCheckOTPForm, self).clean()
        code = cleaned_data['code']
        email = cleaned_data['email']

        if not tokens.password_reset_token_generator.check_token(email, code):
            raise forms.ValidationError(
                message=Messages.INVALID_CODE['message'],
                code=Messages.INVALID_CODE['code']
            )

        return cleaned_data


class ResetPasswordForm(BaseResetPassword):
    """
    This class is used to retrieve the password through e-mail by sending
    the activation code to this e-mail.
    """

    def save(self, request, **kwargs):
        """
        This save() method accepts an optional commit keyword argument,
        which accepts either True or False.
        If you call save() with commit=False,
        then it will return an object that hasn’t yet been saved to the database.
        @return:
        """
        signals.password_reset_send.send(sender=self.user.__class__, request=request, user=self.user)
        return self.user


class SetPasswordForm(BasePasswordCheckOTPForm, AuthSetPasswordForm):
    """
    A form that lets a user change set their password without entering the old
    password
    """

    def __init__(self, user=None, *args, **kwargs):
        super(SetPasswordForm, self).__init__(user, *args, **kwargs)

    def save(self, **kwargs):
        """
        This save() method accepts an optional commit keyword argument,
        which accepts either True or False.
        If you call save() with commit=False,
        then it will return an object that hasn’t yet been saved to the database.
        @return:
        """

        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()
        signals.password_reset_done.send(sender=self.user.__class__, user=self.user)
        return self.user


class ChangeUsernameForm(UserForm):
    """
    This class is used to change email.
    """

    username = forms.CharField(
        label=_("إسم المستخدم"),
        required=True,
        min_length=settings.ACCOUNT_USERNAME_MIN_LENGTH,
        max_length=settings.ACCOUNT_USERNAME_MAX_LENGTH
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if shortcut.filter_all_users_objects_by_kwargs(username=username):
            raise forms.ValidationError(
                message=Messages.USERNAME_IN_USE['message'],
                code=Messages.USERNAME_IN_USE['code']
            )
        return username

    def save(self, **kwargs):
        """
        This save() method accepts an optional commit keyword argument,
        which accepts either True or False.
        If you call save() with commit=False,
        then it will return an object that hasn’t yet been saved to the database.
        @return:
        """
        username = self.cleaned_data.get('username')
        self.user.username = username
        self.user.save()
        return username


class ChangePasswordForm(ChangePasswordForm):
    """
    change user password
    """

    def save(self, **kwargs):
        """
        This save() method accepts an optional commit keyword argument,
        which accepts either True or False.
        If you call save() with commit=False,
        then it will return an object that hasn’t yet been saved to the database.
        @return:
        """
        super(ChangePasswordForm, self).save()
        signals.password_changed.send(sender=self.user.__class__, user=self.user)
        return self.user


class ResendActivateEmail(BaseResetPassword):
    """
    This class is used to resend activate email.
    """

    def clean(self):
        super(ResendActivateEmail, self).clean()
        if self.user.is_verified_email():
            raise forms.ValidationError(
                message=Messages.EMAIL_IS_VERIFIED['message'],
                code=Messages.EMAIL_IS_VERIFIED['code']
            )
        return self.cleaned_data

    def save(self, request, **kwargs):
        """
        This save() method accepts an optional commit keyword argument,
        which accepts either True or False.
        If you call save() with commit=False,
        then it will return an object that hasn’t yet been saved to the database.
        @return:
        """
        signals.resend_activate_email.send(sender=self.user.__class__, request=request, user=self.user)
        return self.user


class ActivateEmail(BasePasswordCheckOTPForm):
    """
    This class is used to activate email.
    """

    def save(self, **kwargs):
        """
        This save() method accepts an optional commit keyword argument,
        which accepts either True or False.
        If you call save() with commit=False,
        then it will return an object that hasn’t yet been saved to the database.
        @return:
        """
        self.user.activate_email()
        signals.activate_email.send(sender=self.user.__class__, user=self.user)
        return self.user


class ChangeEmailForm(UserForm):
    """
    This class is used to change email.
    """

    email = forms.EmailField(
        label=_("البريد الإلكتروني"),
        required=True,
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "placeholder": _("البريد الإلكتروني"),
                "autocomplete": "email",
            }
        )
    )

    role = forms.ChoiceField(
        label=_('نوع المستخدم'),
        choices=USER_MODEL.RoleChoices.choices
    )

    def clean(self):
        email = self.cleaned_data["email"]
        role = self.cleaned_data["role"]
        if shortcut.filter_all_users_objects_by_kwargs(email=email, role=role):
            raise forms.ValidationError(
                message={'email': Messages.EMAIL_IN_USE['message']},
                code=Messages.EMAIL_IN_USE['code']
            )
        return self.cleaned_data

    def save(self, request):
        """
        This save() method accepts an optional commit keyword argument,
        which accepts either True or False.
        If you call save() with commit=False,
        then it will return an object that hasn’t yet been saved to the database.
        @return:
        """
        new_email = self.cleaned_data.get('email')
        old_email = self.user.email

        self.user.change_email(new_email)

        email_address, created = EmailAddress.objects.update_or_create(
            email=old_email, defaults={
                "verified": False, "user": self.user, "email": new_email
            }
        )

        signals.email_changed.send(
            sender=self.user.__class__, request=request, user=self.user,
            from_email_address=old_email, to_email_address=new_email
        )

        return new_email


class RegisterForm(SignupForm):
    """
    This form is used to record the user's information inside the database.
    This form verifies the important and required information in the form
    """

    first_name = forms.CharField(
        label=_('الاسم الأول'),
        required=True
    )

    last_name = forms.CharField(
        label=_('الاسم ألأحير'),
        required=True
    )

    phonenumber = PhoneNumberField(
        label=_('رقم الهاتف'),
        required=True
    )

    def __init__(self, role, *args, **kwargs):
        self.role = role
        super(RegisterForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        """
        this function check if email already use in another user
        @return: email
        """
        email = self.cleaned_data['email']
        if shortcut.filter_all_users_objects_by_kwargs(email=email, role=self.role):
            raise forms.ValidationError(
                message=Messages.EMAIL_IN_USE['message'],
                code=Messages.EMAIL_IN_USE['code']
            )
        return email

    def clean(self):
        """
        this function is used to clean data
        @return:
        """
        super(RegisterForm, self).clean()
        self.cleaned_data.pop('password2', None)
        self.cleaned_data['password'] = self.cleaned_data.pop('password1', None)
        return self.cleaned_data

    def create_user(self, **kwargs):
        """
        this function is used to create user with role
        @param kwargs: another values
        @return: object of user
        """

        if self.role == USER_MODEL.RoleChoices.ADMIN:
            return USER_MODEL.user_objects.create_superuser(**self.cleaned_data)

        return USER_MODEL.user_objects.create_user(role=self.role, **self.cleaned_data)

    def save(self, request, **kwargs):
        """
        This save() method accepts an optional commit keyword argument,
        which accepts either True or False.
        If you call save() with commit=False,
        then it will return an object that hasn’t yet been saved to the database.
        @return:
        """
        user = self.create_user(**kwargs)
        signals.user_signed_up.send(sender=user.__class__, request=request, user=user)
        return user


class ExpoPushTokenForm(forms.Form):
    """
    This form is used to verify the entered token for expo push token
    """

    exponent_push_token = forms.CharField(
        label=_('رمز ألتوكن الخاص بالمستخدم'),
        required=settings.EXPO_PUSH_TOKEN_REQUIRED,
        max_length=settings.EXPO_PUSH_TOKEN_MAX_LENGTH,
        min_length=settings.EXPO_PUSH_TOKEN_MIN_LENGTH,
    )

    def clean_exponent_push_token(self):
        """
        this function used to clean Exponent Push Token and check is valid
        @return: token
        """
        token = self.cleaned_data['exponent_push_token']
        if not token.startswith('ExponentPushToken[') or not token.endswith(']'):
            raise forms.ValidationError(
                message=Messages.EXPONENT_PUSH_TOKEN_FORMAT_ERROR['message'],
                code=Messages.EXPONENT_PUSH_TOKEN_FORMAT_ERROR['code']
            )
        return token

    def save(self, user, **kwargs):
        """
        This save() method accepts an optional commit keyword argument,
        which accepts either True or False.
        If you call save() with commit=False,
        then it will return an object that hasn’t yet been saved to the database.
        @return:
        """
        exponent_push_token = self.cleaned_data['exponent_push_token']
        shortcut.create_exponent_push_token(exponent_push_token, user)
        return exponent_push_token
