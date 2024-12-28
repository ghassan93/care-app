import shortuuid
from django.utils import timezone


def __generate_file(parent_folder, instance, filename):
    """
       @param parent_folder: Represents name of parent folder.
      @param instance: Represents the object of the data model.
      @param filename: Represents the file name of the image.
      @return: Return the path of the image
    """

    filename = f"{shortuuid.uuid()}.{filename.split('.')[-1]}"
    date = timezone.now()
    return f'{parent_folder}/{date.year}/{date.month}/{date.day}/{filename}'


def image_folder(instance, filename):
    """
    @param instance: Represents the object of the data model.
    @param filename: Represents the file name of the image.
    @return: Return the path of the image
    """

    return __generate_file('pictures', instance, filename)


def file_folder(instance, filename):
    """
    @param instance: Represents the object of the data model.
    @param filename: Represents the file name of the file.
    @return: Return the path of the file.
    """

    return __generate_file('files', instance, filename)


class UploadFile(object):
    """
    This class is used to deal with uploading files in the system
    """
    __KEYS = ['files', 'pictures', ]

    def __init__(self, *args, **kwargs):
        super(UploadFile, self).__init__(*args, **kwargs)
        self.CONFIG_CLEAR_DATA = []

    def clear_data(self, clear_data):
        """
        @param clear_data: It is a dictionary that contains a set of fields with their values
        @return: clear_data
        """
        self.CONFIG_CLEAR_DATA = list()
        for key in self.__KEYS:
            self.CONFIG_CLEAR_DATA.append({key: clear_data.pop(key, [])})
        return clear_data

    def handle_uploaded_file(self, instance):
        for clear_data in self.CONFIG_CLEAR_DATA:
            for key, value in clear_data.items():
                if hasattr(instance, key):
                    for data in value:
                        attribute = getattr(instance, key)
                        if isinstance(data, dict):
                            attribute.upload(**data)
                        else:
                            attribute.upload(data)
        return instance