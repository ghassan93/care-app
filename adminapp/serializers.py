from . import mixins


class PasswordChangeSerializer(mixins.PasswordChangeSerializerMixin):
    """
    This class is used to modify a user's password.
    Where the new password is entered with confirm password
    """


class UserSerializer(mixins.UserSerializerMixin):
    """
    This class can handle the add and modify functions of the user model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class VendorSerializer(mixins.VendorSerializerMixin):
    """
    This class can handle the add and modify functions of the vendor model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class CommentSerializer(mixins.CommentSerializerMixin):
    """
    This class can handle the add and modify functions of the  comment model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class ServiceSerializer(mixins.ServiceSerializerMixin):
    """
    This class can handle the add and modify functions of the service model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class WithdrawRequestSerializer(mixins.WithdrawRequestSerializerMixin):
    """
    This class can handle the add and modify functions of the withdrawal request model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class OfferSerializer(mixins.OfferSerializerMixin):
    """
This class can handle the add and modify functions of the offer request model and
return all the objects associated with this table.
This class represents an abstract class that you can use in any app you want
and modify the functions through inheritance operations
"""


class ActiveOfferSerializer(mixins.ActiveOfferSerializerMixin):
    """
    This class is used to activate discount codes that have been added
    via the control panel.
    Where a discount code is sent to all developer accounts within the system,
    and through this code, he can activate the discount code that was created
    """


class CitySerializer(mixins.CitySerializerMixin):
    """
    This class can handle the add and modify functions of the city model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class PoliciesSerializer(mixins.PoliciesSerializerMixin):
    """
    This class can handle the add and modify functions of the policies model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class TagSerializer(mixins.TagSerializerMixin):
    """
    This class can handle the add and modify functions of the tag model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class BannerSerializer(mixins.BannerSerializerMixin):
    """
    This class can handle the add and modify functions of the banner model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class OrderSerializer(mixins.OrderSerializerMixin):
    """
    This class can handle the add and modify functions of the order model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class InvoiceSerializer(mixins.InvoiceSerializerMixin):
    """
    This class can handle the add and modify functions of the invoice model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class WalletSerializer(mixins.WalletSerializerMixin):
    """
    This class can handle the add and modify functions of the wallet model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class DepositSerializer(mixins.DepositSerializerMixin):
    """
    This class is used to withdraw an amount from the user's wallet.
    where the value to be withdrawn is passed,
    it must be a valid value in order to complete the operation.
    """


class WithdrawSerializer(mixins.WithdrawSerializerMixin):
    """
    This class is used to deposit an amount into the private wallet
    where the value to be deposited is passed, it must be a valid value in order to complete the operation
    """


class NotificationSerializer(mixins.NotificationSerializerMixin):
    """
    This class is used to send notifications to registered users.
    the user type is passed along with the message header and body.
    """
