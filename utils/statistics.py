from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, Trunc
from django.utils import timezone

today = timezone.now()


def filter_daily(queryset, lookup, **kwargs):
    return queryset.filter(**{
        '{}__year'.format(lookup): today.year,
        '{}__month'.format(lookup): today.month,
        '{}__range'.format(lookup): (today - timedelta(1), today)
    }, **kwargs)


def filter_weekly(queryset, lookup, **kwargs):
    return queryset.filter(**{
        '{}__year'.format(lookup): today.year,
        '{}__month'.format(lookup): today.month,
        '{}__range'.format(lookup): (today - timedelta(7), today)
    }, **kwargs)


def filter_monthly(queryset, lookup, **kwargs):
    return queryset.filter(**{
        '{}__year'.format(lookup): today.year,
        '{}__month'.format(lookup): today.month
    }, **kwargs)


def filter_yearly(queryset, lookup, **kwargs):
    return queryset.filter(**{
        '{}__year'.format(lookup): today.year,
    }, **kwargs)


def filter_gte(queryset, lookup, **kwargs):
    return queryset.filter(Q(**{'{}__gte'.format(lookup): today}, **kwargs))


def filter_lte(queryset, lookup, **kwargs):
    return queryset.filter(Q(**{'{}__lte'.format(lookup): today}, **kwargs))


def filter_range_date(queryset, lookup_start_date, lookup_end_date=None, **kwargs):
    return queryset.filter(
        Q(**{'{}__lte'.format(lookup_start_date): today}) &
        Q(**{'{}__gte'.format(lookup_end_date): today}) &
        Q(**kwargs)
    )


def filter_date(filter_type, queryset, lookup1, **kwargs):
    if filter_type == 'daily':
        return filter_daily(queryset, lookup1, **kwargs)
    elif filter_type == 'weekly':
        return filter_weekly(queryset, lookup1, **kwargs)
    elif filter_type == 'monthly':
        return filter_monthly(queryset, lookup1, **kwargs)
    elif filter_type == 'yearly':
        return filter_yearly(queryset, lookup1, **kwargs)
    elif filter_type == 'range_date':
        return filter_range_date(queryset, lookup1, **kwargs)
    return queryset


class ConstantStatisticDictionary:

    def __init__(self, query, serializer, lookup, date=None):
        self.query = query
        self.serializer = serializer
        self.lookup = lookup
        self.today = date or timezone.now()

    YEAR_CHART = {
        'JAN': 0, 'FEB': 0, 'MAR': 0,
        'APR': 0, 'MAY': 0, 'JUN': 0,
        'JUL': 0, 'AUG': 0, 'SEP': 0,
        'OCT': 0, 'NOV': 0, 'DEC': 0
    }
    MONTH_CHART = {
        '01': 0, '02': 0, '03': 0,
        '04': 0, '05': 0, '06': 0,
        '07': 0, '08': 0, '09': 0,
        '10': 0, '11': 0, '12': 0,
        '13': 0, '14': 0, '15': 0,
        '16': 0, '17': 0, '18': 0,
        '19': 0, '20': 0, '21': 0,
        '22': 0, '23': 0, '24': 0,
        '25': 0, '26': 0, '27': 0,
        '28': 0, '29': 0, '30': 0,
        '31': 0}
    WEEK_CHART = {
        'MON': 0, 'TUE': 0, 'WED': 0,
        'THU': 0, 'FRI': 0, 'SAT': 0,
        'SUN': 0
    }
    CHART_TYPE = {
        'year': [TruncMonth, YEAR_CHART, '%b'],
        'month': [Trunc, MONTH_CHART, '%d'],
        'week': [Trunc, WEEK_CHART, '%a']
    }

    @classmethod
    def __fillOut(cls, queryset, chart: dict, time_parameter: str):
        """

        :param queryset: query contain multi object
        :param chart: type of char  year_chart, month_chart, week_chart
        :param time_parameter: is [%b, %d, %a]
        :return chart:
        """
        chart = chart.copy()
        for row in queryset:
            key = row.get('data').strftime(time_parameter).upper()
            value = row.get('count')
            if key in chart.keys():
                chart[key] = chart.get(key) + value
        return chart

    def __annotate(self, trunc, *parameter_trunc: tuple, **filters: dict):
        """
        :param trunc: TruncMonth or Trunc Function for get days in
                      queryset.
        :param parameter_trunc:  parameters in TruncMonth or Trunc Function
        :param filters: condition in filter queryset>
        :return QuerySet:
        """
        return self.query.filter(**filters).annotate(
            data=trunc(*parameter_trunc)).values(
            'data').annotate(
            count=Count('id')
        ).values('data', 'count')

    def Chart(self, chart_type: str, *parameter_trunc, **filters: dict):

        """

        :param chart_type: is the type of chart [year, month, week]
        :param parameter_trunc:  parameters in TruncMonth or Trunc Function
        :param filters: condition in filter queryset>
        """
        chart_type = chart_type.lower()
        if chart_type not in self.CHART_TYPE.keys():
            raise ValueError('The input is not support.')

        chart = self.CHART_TYPE[chart_type]
        queryset = self.__annotate(chart[0], *parameter_trunc, **filters)
        data = self.__fillOut(queryset, chart[1], chart[2])
        return data


class StatisticsData(ConstantStatisticDictionary):

    def filter(self, attr, value):
        return self.query.filter(**{attr: value})

    def aggregate(self, attr, value):
        return self.query.aggregate(**{attr: value})

    def annotate(self, attr, value):
        return self.query.annotate(**{attr: value})

    def get_serializer_data(self):
        return self.serializer(self.query, many=True)

    def count_objects(self):
        return self.query.count()

    def count_filter(self, attr, value):
        return self.filter(attr, value).count()

    def statisticsInYear(self, condition=None):
        return self.Chart(
            'year',
            self.lookup,
            **{'{}__year'.format(self.lookup): condition if condition else self.today.year}
        )

    def statisticsInLastYear(self):
        return self.statisticsInYear(self.today.year - 1)

    def statisticsInMonth(self, condition=None):
        return self.Chart(
            'month',
            self.lookup,
            'day',
            **{
                '{}__year'.format(self.lookup): self.today.year,
                '{}__month'.format(self.lookup): condition if condition else self.today.month
            }
        )

    def statisticsInLastMonth(self):
        return self.statisticsInMonth(self.today.month - 1)

    def statisticsInWeek(self, start=None, end=None):
        return self.Chart(
            'week',
            self.lookup,
            'day',
            **{
                '{}__year'.format(self.lookup): self.today.year,
                '{}__month'.format(self.lookup): self.today.month,
                '{}__range'.format(self.lookup): (
                    start if start else self.today - timedelta(7),
                    end if end else self.today
                )
            }
        )

    def statisticsInLastWeek(self):
        return self.statisticsInWeek(
            self.today - timedelta(7 * 2),
            self.today - timedelta(7),
        )

    def get_statistics_data(self, prefix='object'):
        """
        This function get all statistics (year - month -week) and return it
        @param prefix: the name of key in dict
        @return: dict
        """
        context = dict()
        context[f'{prefix}_this_week'] = self.statisticsInWeek().values()
        context[f'{prefix}_last_week'] = self.statisticsInLastWeek().values()
        context[f'{prefix}_this_month'] = self.statisticsInMonth().values()
        context[f'{prefix}_last_month'] = self.statisticsInLastMonth().values()
        context[f'{prefix}_this_year'] = self.statisticsInYear().values()
        context[f'{prefix}_last_year'] = self.statisticsInLastYear().values()
        return context
