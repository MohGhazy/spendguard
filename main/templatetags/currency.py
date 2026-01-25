from django import template

register = template.Library()

@register.filter
def rupiah(value):
 try:
  value = float(value)
  return "Rp{:,.0f}".format(value).replace(",", ".")
 except:
  return value
