from django.db import models


class PhoneManager(models.Manager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def phones(self, phone_type, **kwargs):
        """
        filter phonenumber using phone type
        @param phone_type: the phone type
        @param kwargs: any filters
        @return: Queryset
        """
        return self.filter(phone_type=phone_type, **kwargs)

    def fax(self):
        return self.phones(self.model.PhoneTypeChoices.FAX)

    def home(self):
        return self.phones(self.model.PhoneTypeChoices.HOME)

    def mobile(self):
        return self.phones(self.model.PhoneTypeChoices.MOBILE)

    def work(self):
        return self.phones(self.model.PhoneTypeChoices.WORK)

    def create_generic_object(self, number, **kwargs):
        instance = self.create(number=number, **kwargs)
        instance.primary = self.all().count() == 1
        instance.save()
        return instance


class PictureManager(models.Manager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    def create_generic_object(self, picture_file, **kwargs):
        """
        This function is used to create an object of type picture, which receives the
        following parameters:
        @param picture_file: physical picture
        """
        return self.create(picture_file=picture_file, **kwargs)
