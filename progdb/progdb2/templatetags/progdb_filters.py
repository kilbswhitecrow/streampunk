from django import template
from progdb.progdb2.models import Item, Person, Room, Tag
from django.utils.html import escape

register = template.Library()

@register.filter
def linky(value, text=None):
  if not text:
    text = value
  return '<a href="%s">%s</a>' % (value.get_absolute_url(), escape(text))

@register.filter
def linky2(value, prev):
  pid = prev.id
  pname = prev.__class__.__name__.lower()
  id = value.id
  name = value.__class__.__name__.lower()
  return '<a href="/progdb/%s/%d/%s/%d/">%s</a>' % (pname, pid, name, id, escape(value))
