from django import forms


class PartialUpdateForm(forms.ModelForm):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not args:
            args = kwargs.get('data')
        elif isinstance(args, tuple):
            args = list(args)[0]
        else:
            args = args[-1]

        self.cleanup_missing_keys(args)

    def cleanup_missing_keys(self, data: dict):
        """
        Removes missing keys from fields on form submission.
        This avoids resetting fields that are not present in
        the submitted data, which may be the sign of a buggy
        or incomplete template.
        Note that this cleanup relies on the HTML form being
        patched to send all keys, even for checkboxes, via
        input[type="hidden"] fields or some JS magic.
        """

        if data is None:
            # not a form submission, don't modify self.fields
            return

        got_keys = data.keys()
        field_names = self.fields.keys()
        for missing in set(field_names) - set(got_keys):
            del self.fields[missing]