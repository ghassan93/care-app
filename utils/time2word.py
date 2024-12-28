from django.utils.translation import ugettext_lazy as _


class Time2Word(object):
    """
    Given a time in the format of hh:mm (12-hour format) 0 < hh < 12, 0 <= mm < 60.
    The task is to convert it into words as shown:
    """

    ALPHA = [_('دقيقة'), _('نص ساعة'), _('ساعة'), _('ساعتين'), _('ساعات')]

    def __init__(self, hour, minute):
        """

        @param hour: the hour of the time
        @param minute: the minute of the time
        """
        if not hour and not minute:
            raise ValueError('the time is not support')
        if hour < 0 or hour > 12:
            raise ValueError('the hour is not support')

        if minute not in [0, 15, 30, 45]:
            raise ValueError('the hour is not support')

        self.hour = hour
        self.minute = minute

    def get_hour(self):
        if self.hour == 1:
            return self.ALPHA[-3]
        elif self.hour == 2:
            return self.ALPHA[-2]
        elif 3 <= self.hour <= 10:
            return '{} {}'.format(self.hour, self.ALPHA[-1])
        elif 11 <= self.hour <= 12:
            return '{} {}'.format(self.hour, self.ALPHA[-3])
        return ''

    def get_minute(self):
        if self.hour and self.minute:
            return '{} {}'.format(self.minute, self.ALPHA[0])
        elif self.minute == 30:
            return self.ALPHA[1]
        elif self.minute:
            return '{} {}'.format(self.minute, self.ALPHA[0])
        return ''

    def format(self):
        h = self.get_hour()
        m = self.get_minute()

        if h and m:
            return '{} {} {}'.format(h, _('و'), m)

        return h or m
