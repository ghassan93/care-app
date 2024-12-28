from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django_softdelete.models import SoftDeleteQuerySet
from random_username.generate import generate_username


class UserManager(BaseUserManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """
        return email.lower()

    def _create_user(self, username: str, email: str, password: str, role: str, **kwargs):
        """
          Creates and saves a superuser with the given email,
          username and password.
          @:param username: is the username for user
          @:param email: is the email for user
          @:param phone: is the phone number for user
          @:param password: is the password for user
          @:param role: is the user type  for user
          @:param extra_fields: this is the extra attributes like first name or
          last name
          @:returns new user
        """
        if not username:
            username = generate_username(1)[0]

        email = self.normalize_email(email)
        username = self.model.normalize_username(username)

        user = self.model(username=username, email=email, role=role, **kwargs)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.set_role(role)

        user.save(using=self._db)

        return user

    def create_user(self, username: str = None, email: str = None, password: str = None, role: str = None, **kwargs):
        """
          Creates and saves a superuser with the given email,
          username and password.
          @:param username: is the username for user
          @:param email: is the email for user
          @:param password: is the password for user
          @:param role: is the user type  for user
          @:param extra_fields: this is the extra attributes like first name or
          last name
          @:returns new user
        """
        user = self._create_user(username=username, email=email, password=password, role=role, **kwargs)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str = None, email: str = None, password: str = None, **kwargs):
        """
          Creates and saves a superuser with the given email,
          username and password.
          @:param username: is the username for user
          @:param email: is the email for user
          @:param password: is the password for user
          @:param role: is the user type  for user
          @:param extra_fields: this is the extra attributes like first name or
          last name
          @:returns new user
        """

        user = self._create_user(
            username=username, email=email, password=password,
            role=self.model.RoleChoices.ADMIN, **kwargs
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def role(self, role, **filters):
        """
        This method is used for the filter of users based on the type of user
        passed from the variable with the name role
        @param role:The name of the role that the user holds
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.filter(role=role, **filters)

    def admins(self, **filters):
        """
        This method returns users with administrator role
        @return: QuerySet
        """
        return self.role(self.model.RoleChoices.ADMIN, is_superuser=True, is_staff=True, **filters)

    def vendors(self, **filters):
        """
        This method returns users with vendors role
        @return: QuerySet
        """
        return self.role(self.model.RoleChoices.VENDOR, **filters)

    def customers(self, **filters):
        """
        This method returns users with customers role
        @return: QuerySet
        """
        return self.role(self.model.RoleChoices.CUSTOMER, **filters)

    def users_for_vendor(self, vendor):
        """
        this function is used ro return all users for custom vendor
        @param vendor: custom vendor
        @return: queryset
        """
        return self.vendors(vendor_user__vendor=vendor)


class UserUndeletedManager(UserManager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def get_queryset(self):
        """
        This function if final filter function in ORM.
        @return: Queryset
        """
        return SoftDeleteQuerySet(model=self.model, using=self._db).filter(is_deleted=False)


class ExponentPushTokenManager(models.Manager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def create_or_update(self, receiver_token, user, **kwargs):
        """
        This function is used to create or update receiver_token in database
        @param receiver_token: the token of mobil
        @param user: the user object
        @param kwargs: dict of filters
        @return object
        """
        qs = self.get_queryset().filter(receiver_token=receiver_token)

        if qs.exists():
            return qs.update(
                receiver_token=receiver_token, user=user,
                is_active=True, activated_at=timezone.now()
            )

        return self.create(receiver_token=receiver_token, user=user, **kwargs)

    def tokens(self, is_active, **filters):
        """
        This method is used for the filter of users based on the type of user
        passed from the variable with the name role
        @param is_active:The value of active
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.filter(is_active=is_active, **filters)

    def actives(self):
        return self.tokens(is_active=True)

    def archives(self):
        return self.tokens(is_active=False)


class AddressManager(models.Manager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def all_address(self, user, **filters):
        """
        This method is used for the filter of addresses based on the user
        passed from the variable with the name user
        @param user:the custom user
        @param filters: Dictionary of different fields
        @return: QuerySet
        """
        return self.filter(user=user, **filters)
