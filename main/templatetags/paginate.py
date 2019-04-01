from django import template

register = template.Library()


@register.inclusion_tag("paginate.html", takes_context=True)
def paginate(context):
    return context
