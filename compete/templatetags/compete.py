from django import template

register = template.Library()


@register.inclusion_tag("compete/run_list.html", takes_context=True)
def run_list(context, runs):
    return dict(runs=runs, user=context['user'])
