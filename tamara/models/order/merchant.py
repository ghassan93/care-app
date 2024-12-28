class Merchant(object):
    """
    This class is used to represent merchant as it consists of success, failure, cancel and others.
    """

    SUCCESS = 'success'
    FAILURE = 'failure'
    CANCEL = 'cancel'
    NOTIFICATION = 'notification'

    def __init__(self, success: str, failure: str, cancel: str, notification: str):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.success = success
        self.failure = failure
        self.cancel = cancel
        self.notification = notification

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.SUCCESS: self.success,
            self.FAILURE: self.failure,
            self.CANCEL: self.cancel,
            self.NOTIFICATION: self.notification,
        }

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        success = dictionary.get(cls.SUCCESS)
        failure = dictionary.get(cls.FAILURE)
        cancel = dictionary.get(cls.CANCEL)
        notification = dictionary.get(cls.NOTIFICATION)

        # Return an object of this model
        return cls(success=success, failure=failure, cancel=cancel, notification=notification)
