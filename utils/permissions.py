from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from vendorapp.models import VendorTypeChoice


class IsAnonymous(permissions.BasePermission):
    """
    permission to only allow to Anonymous User.
    """

    def has_permission(self, request, view):
        return bool(request.user.is_anonymous)


class IsAuthenticated(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_verified and
            (request.user.vendor_user.is_verified if request.user.is_vendor else True)

        )


class IsAdmin(permissions.BasePermission):
    """
    permission to only allow to admin User.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_verified and
            request.user.is_admin
        )


class IsAdminOrAnonymous(permissions.BasePermission):
    """
    permission to only allow to Anonymous User.
    """

    def has_permission(self, request, view):
        return bool(
            request.user.is_anonymous or
            (
                    request.user and
                    request.user.is_authenticated and
                    request.user.is_verified and
                    request.user.is_admin
            )

        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
     The request is admin as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and
            request.user.is_verified and
            request.user.is_admin
        )


class IsVendor(permissions.BasePermission):
    """
    permission to only allow to admin User.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_verified and
            request.user.is_vendor and
            request.user.vendor_user.is_verified
        )


class IsSelfCareVendor(permissions.BasePermission):
    """
    permission to only allow to admin User.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_verified and
            request.user.is_vendor and
            request.user.vendor_user.is_verified and
            request.user.vendor_user.vendor.vendor_type == VendorTypeChoice.SELF_CARE,

        )


class IsCarCareVendor(permissions.BasePermission):
    """
    permission to only allow to admin User.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_verified and
            request.user.is_vendor and
            request.user.vendor_user.is_verified and
            request.user.vendor_user.vendor.vendor_type == VendorTypeChoice.CAR_CARE

        )


class IsCustomer(permissions.BasePermission):
    """
    permission to only allow to admin User.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_verified and
            request.user.is_customer
        )
