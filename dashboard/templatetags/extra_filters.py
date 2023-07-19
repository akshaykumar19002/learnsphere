from django import template

register = template.Library()

@register.filter
def times(number):
    try:
        number = int(number)
    except:
        number = 0
    return range(int(number))

@register.filter
def range_to(number):
    try:
        number = int(number)
    except:
        number = 0
    return range(int(number), 5)
