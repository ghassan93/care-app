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


class CommentSerializer(mixins.CommentSerializerMixin):
    """
    This class can handle the add and modify functions of the  comment model and
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


class WalletSerializer(mixins.WalletSerializerMixin):
    """
    This class can handle the add and modify functions of the wallet model and
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


class CreateOrderScheduleSerializer(mixins.CreateOrderScheduleSerializerMixin):
    """
    This class is used to add an order of a scheduled type where
    the availability number is entered with the start time and end time
    """


class CreateOrderUnscheduleSerializer(mixins.CreateOrderUnscheduleSerializerMixin):
    """
      This class is used to add an order of an unscheduled type where
      the service is passed directly without adding availability
      """


class OfferCodeSerializer(mixins.OfferCodeSerializerMixin):
    """
    This class is used to verify the discount code by passing the code with
    the owner of this discount
    """


class WalletPaymentSerializer(mixins.WalletPaymentSerializerMixin):
    """
    This class is used in the payment process through the wallet,
    where the value of the paid amount is verified.
    If the wallet does not have enough amount, an error is returned
    """


class AlrajhiGetPageURLSerializer(mixins.AlrajhiGetPageURLSerializerMixin):
    """
    This class is used through payment via Al-Rajhi,
    as it returns the Al-Rajhi page with the appropriate amount for
    the payment process
    """


class AlrajhiPaymentSerializer(mixins.AlrajhiPaymentSerializerMixin):
    """
    This class is used to confirm the payment process through Al-Rajhi,
    as the data is returned through the Al-Rajhi gateway
    """


class TamaraGetPageURLSerializer(mixins.TamaraGetPageURLSerializerMixin):
    """
    This class is used to confirm the payment process through Tamara,
    as the data is returned through the Tamara gateway
    """


class TamaraPaymentSerializer(mixins.TamaraPaymentSerializerMixin):
    """
    This class is used to confirm the payment process through Tamara,
    as the data is returned through the Tamara gateway
    """
