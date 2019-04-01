from django import template

register = template.Library()


@register.inclusion_tag("compete/run_list.html")
def run_list(runs):
    return dict(runs=runs)
