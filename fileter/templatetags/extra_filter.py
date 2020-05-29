from django.template.library import Library
from django.template.defaultfilters import stringfilter

register = Library()


@register.filter(is_safe=True)
def money(value, arg):
    return value * arg





