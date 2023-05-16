import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def custom_markdown(value):
    extensions = [
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ]
    if not value:
        return ''
    else:
        return mark_safe(markdown.markdown(value, extensions=extensions))
