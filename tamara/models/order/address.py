class Address(object):
    """
    This class is used to represent address as it consists of first_name, last_name, line1 and others.
    """

    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'
    LINE1 = 'line1'
    LINE2 = 'line2'
    REGION = 'region'
    POSTAL_CODE = 'postal_code'
    CITY = 'city'
    COUNTRY_CODE = 'country_code'
    PHONE_NUMBER = 'phone_number'

    def __init__(
            self,
            first_name: str,
            last_name: str,
            line1: str,
            city: str,
            country_code: str,
            line2: str = None,
            region: str = None,
            postal_code: str = None,
            phone_number: str = None
    ):
        """
        When you create a new object of a class, Python automatically calls the __init__() method to
        initialize the object’s attributes.
        """
        self.first_name = first_name
        self.last_name = last_name
        self.line1 = line1
        self.city = city
        self.country_code = country_code
        self.line2 = line2
        self.region = region
        self.postal_code = postal_code
        self.phone_number = phone_number

    def to_dictionary(self):
        """
        Return the property of the object as a dictionary
        """
        return {
            self.FIRST_NAME: self.first_name,
            self.LAST_NAME: self.last_name,
            self.PHONE_NUMBER: self.phone_number,
            self.LINE1: self.line1,
            self.LINE2: self.line2,
            self.CITY: self.city,
            self.REGION: self.region,
            self.POSTAL_CODE: self.postal_code,
            self.COUNTRY_CODE: self.country_code,
        }

    @classmethod
    def from_dictionary(cls, dictionary: dict):
        """
        Creates an instance of this model from a dictionary
        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        first_name = dictionary.get(cls.FIRST_NAME)
        last_name = dictionary.get(cls.LAST_NAME)
        phone_number = dictionary.get(cls.PHONE_NUMBER, None)

        line1 = dictionary.get(cls.LINE1)
        line2 = dictionary.get(cls.LINE2, None)

        city = dictionary.get(cls.CITY)
        country_code = dictionary.get(cls.COUNTRY_CODE)
        region = dictionary.get(cls.REGION, None)
        postal_code = dictionary.get(cls.POSTAL_CODE, None)

        # Return an object of this model
        return cls(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            line1=line1,
            line2=line2,
            city=city,
            country_code=country_code,
            region=region,
            postal_code=postal_code,
        )
