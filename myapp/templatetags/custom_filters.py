from django import template

register = template.Library()

@register.filter(name='mul')
def mul(value, arg):
    """
    Multiply the arg and value
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='div')
def div(value, arg):
    """
    Divide the value by the arg
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0 