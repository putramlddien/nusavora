from django import template

register = template.Library()

@register.filter
def inisial(full_name):
    if not full_name:
        return ''
    parts = full_name.strip().split()
    initials = ''.join(part[0].upper() for part in parts[:2])
    return initials
