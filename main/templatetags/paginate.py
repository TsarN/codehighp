from django import template

register = template.Library()


@register.inclusion_tag("paginate.html", takes_context=True)
def paginate(context, page_obj=None):
    if not page_obj:
        return context
    else:
        return dict(page_obj=page_obj)
