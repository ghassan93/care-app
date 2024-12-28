from . import mixins


class TagSerializer(mixins.TagSerializerMixin):
    """
    This class can handle the add and modify functions of the tag model and
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


class BannerSerializer(mixins.BannerSerializerMixin):
    """
    This class can handle the add and modify functions of the banner model and
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


class EmployeeSerializer(mixins.EmployeeSerializerMixin):
    """
    This class can handle the add and modify functions of the employee model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class AvailabilitySerializer(mixins.AvailabilitySerializerMixin):
    """
    This class can handle the add and modify functions of the availability model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class BankAccountSerializer(mixins.BankAccountSerializerMixin):
    """
    This class can handle the add and modify functions of the bank model and
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


class OrderItemSerializer(mixins.OrderItemSerializerMixin):
    """
    This class can handle the add and modify functions of the order item model and
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
