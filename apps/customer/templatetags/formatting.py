from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def rupiah(value):
    try:
        value = float(value)
        return f"Rp {intcomma(int(value))}"
    except:
        return value
