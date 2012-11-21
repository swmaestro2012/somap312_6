from django.template import Library
import datetime

register = Library()

@register.filter(expects_localtime=True)
def epoch_to_datetime(value):
    if isinstance(value, int):
        return datetime.datetime.fromtimestamp(value/1000.0)
    return ''
