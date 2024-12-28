from authapp.forms import ChangePasswordForm


class ChangePasswordForm(ChangePasswordForm):
    """
    change user password
    """

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields.pop('oldpassword')