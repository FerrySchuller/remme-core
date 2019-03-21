from wtforms import validators


class StringTypeRequired(object):
    """
    Validates the value for the required type.

    Args:
        message (str): error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):

        if not isinstance(field.data, str):
            if self.message is None:
                message = field.gettext('This field is required.')
            else:
                message = self.message

            field.errors[:] = []
            raise validators.StopValidation(message)


class DataRequired(object):
    """
    Checks the field's data is 'truthy' otherwise stops the validation chain.

    This validator checks that the ``data`` attribute on the field is a 'true'
    value (effectively, it does ``if field.data``.) Furthermore, if the data
    is a string type, a string containing only whitespace characters is
    considered false.

    If the data is zero, WTForms validators.DataRequired considers it like False
    and response is like argument is missed. We need not missed argument error message,
    but invalid data error message. So appeared the opportunity to write сustom
    validator to solve this case.

    If the data is empty, also removes prior errors (such as processing errors)
    from the field.

    Args:
        message (str): error message to raise in case of a validation error.
    """

    field_flags = ('required',)

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):

        if field.data == 0:
            return

        elif not field.data or isinstance(field.data, str) and not field.data.strip():
            if self.message is None:
                message = field.gettext('This field is required.')
            else:
                message = self.message

            field.errors[:] = []
            raise validators.StopValidation(message)


class Optional(object):
    """
    Allows empty input and stops the validation chain from continuing.

    If input is empty, also removes prior errors (such as processing errors)
    from the field.

    Args:
        message (str): error message to raise in case of a validation error.
        strip_whitespace: if True (the default) also stop the validation
        chain on input which consists of only whitespace.
    """

    field_flags = ('optional',)

    def __init__(self, message=None, strip_whitespace=True):
        self.message = message
        if strip_whitespace:
            self.string_check = lambda s: s.strip()
        else:
            self.string_check = lambda s: s

    def __call__(self, form, field):
        if not field.raw_data or isinstance(field.raw_data[0], str) and not self.string_check(field.raw_data[0]):
            field.errors[:] = []
            raise validators.StopValidation(self.message)
