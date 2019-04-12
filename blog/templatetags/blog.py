from django import template

register = template.Library()


@register.inclusion_tag('blog/post.html', takes_context=True)
def post(context, x, short=False):
    return dict(post=x, short=short, user=context['user'])
