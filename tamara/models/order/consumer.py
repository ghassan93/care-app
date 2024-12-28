class Consumer(object):
    """
    This class is used to represent customer as it consists of first_name, last_name, phone_number and others.
    """

    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'
    PHONE_NUMBER = 'phone_number'
    EMAIL = 'email'

    def __init__(self, first_name: str, last_name: str, phone_number: str, email: str):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email = email

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.FIRST_NAME: self.first_name,
            self.LAST_NAME: self.last_name,
            self.PHONE_NUMBER: self.phone_number,
            self.EMAIL: self.email
        }

    @classmethod
    def form_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        first_name = dictionary.get(cls.FIRST_NAME)
        last_name = dictionary.get(cls.LAST_NAME)
        phone_number = dictionary.get(cls.PHONE_NUMBER)
        email = dictionary.get(cls.EMAIL)

        # Return an object of this model
        return cls(first_name=first_name, last_name=last_name, phone_number=phone_number, email=email)
