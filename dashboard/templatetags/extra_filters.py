from django import template

register = template.Library()

@register.filter
def times(number):
    return range(int(number))

@register.filter
def range_to(number):
    return range(int(number), 5)
