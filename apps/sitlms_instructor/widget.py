from django import forms

class DatePickerInput(forms.DateInput):
        input_type = 'date'

class TimePickerInput(forms.TimeInput):
        input_type = 'time'

class DateTimePickerInput(forms.DateTimeInput):
        input_type = 'datetime'

class SplitDateTimeWidget(forms.SplitDateTimeWidget):
    """
    A widget that splits datetime input into two <input type="text"> boxes,
    and uses HTML5 'date' and 'time' inputs.
    """

    def __init__(self, attrs=None, date_format=None, time_format=None, date_attrs=None, time_attrs=None):
        date_attrs = date_attrs or {}
        time_attrs = time_attrs or {}
        if "type" not in date_attrs:
            date_attrs["type"] = "date"
        if "type" not in time_attrs:
            time_attrs["type"] = "time"
        return super().__init__(
            attrs=attrs, date_format=date_format, time_format=time_format, date_attrs=date_attrs, time_attrs=time_attrs
        )


class SplitDateTimeField(forms.SplitDateTimeField):
    widget = SplitDateTimeWidget