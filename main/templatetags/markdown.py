from django import template
import markdown2
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def markdown(value):
    return mark_safe(markdown2.markdown(value))
