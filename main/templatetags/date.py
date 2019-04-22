from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def utc_date(value):
    return value.strftime("%d %b %Y %H:%M UTC")
