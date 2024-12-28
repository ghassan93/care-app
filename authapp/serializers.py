from . import mixins


class LoginSerializer(mixins.LoginSerializerMixin):
    """
    This class is used to log the user into the system.
    Where the username and password are passed,
    and then this class verifies the user data and returns the appropriate response.
    """


class PasswordResetSerializer(mixins.PasswordResetSerializerMixin):
    """
    This class is used to reset a user's password. Where he must enter the user's email and role,
    and then this class verifies the information and sends an alert to the e-mail
    associated with this user
    """


class PasswordCheckOTPSerializer(mixins.PasswordCheckOTPSerializerMixin):
    """
    This class is used to verify the code sent to the email.
    Where the e-mail, user role and code are entered,
    and then this class verifies the validity of the data.
    """


class SetPasswordSerializer(mixins.SetPasswordSerializerMixin):
    """
    This class is used to assign a new password by entering the user's email address,
    role, and verification code with the new password
    """


class UsernameChangeSerializer(mixins.UsernameChangeSerializerMixin):
    """
    This class is used to modify the username by passing the current user
    with the new username.
    """


class EmailChangeSerializer(mixins.EmailChangeSerializerMixin):
    """
    This class is used to modify the username by passing the current user
    with the new username.
    """


class PasswordChangeSerializer(mixins.PasswordChangeSerializerMixin):
    """
    This class is used to modify a user's password.
    Where the old password is entered with the new password and confirm password
    """


class ProfileSerializer(mixins.ProfileSerializerMixin):
    """
    This class can handle the add and modify functions of the profile model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class AddressSerializer(mixins.AddressSerializerMixin):
    """
    This class can handle the add and modify functions of the address model and
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


class UserSerializer(mixins.UserSerializerMixin):
    """
    This class can handle the add and modify functions of the user model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class EmailCheckOTPSerializer(mixins.EmailCheckOTPSerializerMixin):
    """
    This class is used to verify the code sent to the email.
    Where the e-mail, user role and code are entered,
    and then this class verifies the validity of the data.
    """


class ResenActivateEmailSerializer(mixins.ResenActivateEmailSerializerMixin):
    """
    This class is used to resend the verification code to the e-mail
    by passing the e-mail with the user's roller
    """


class ActivateEmailSerializer(mixins.ActivateEmailSerializerMixin):
    """
    This class is used to activate the user's e-mail by passing the e-mail and
    the user's roll with the code sent to the e-mail
    """


class UserDeletionSerializer(mixins.UserDeletionSerializerMixin):
    """
    This class can handle the add and modify functions of the user deletion model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """


class NotificationSerializer(mixins.NotificationSerializerMixin):
    """
    This class can handle the add and modify functions of the notification model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations.
    And class is used to send notifications to users by passing the user's roll
    with the letter address and the text of the message.
    where these classes use the Expo to send notifications
    """


class ExpoPushTokenSerializer(mixins.ExpoPushTokenSerializerMixin):
    """
    This class can handle the add and modify functions of the expo push token model and
    return all the objects associated with this table.
    This class represents an abstract class that you can use in any app you want
    and modify the functions through inheritance operations
    """
