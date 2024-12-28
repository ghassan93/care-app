class Base(object):
    """
    This class should not be instantiated but should be used as a base class
    """

    properties = {}

    def to_dict(self):
        """
        Return the property of the object as a dictionary
        """
        raise NotImplementedError("Please Implement this method")

    @classmethod
    def form_dict(cls, data: dict):
        """
        Create and return a new object.
        """
        raise NotImplementedError("Please Implement this method")

    @classmethod
    def getmembers(cls):
        """
        This module provides a method called getmemebers()
        that returns a list of class attributes and methods.
        """
        raise NotImplementedError("Please Implement this method")


class BaseObject(Base):
    """
    This class should not be instantiated but should be used as a base class
    """

    @classmethod
    def getmembers(cls):
        """
        This module provides a method called getmemebers()
        that returns a list of class attributes and methods.
        """
        raise NotImplementedError("Please Implement this method")
