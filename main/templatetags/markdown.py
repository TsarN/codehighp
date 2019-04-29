import re

from django import template
import markdown2
from django.utils.safestring import mark_safe

from users.models import CustomUser

register = template.Library()


@register.filter
def markdown(value):
    value = markdown2.markdown(value, safe_mode='escape', extras=["fenced-code-blocks"])
    usernames = list(set(re.findall(r'\[user:([a-zA-Z0-9]+?)\]', value)))
    for user in CustomUser.objects.filter(username__in=usernames):
        value = value.replace('[user:%s]' % user.username, user.html_link)
    return mark_safe(value)
