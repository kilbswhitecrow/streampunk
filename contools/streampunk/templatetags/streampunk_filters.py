# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2012 Stephen Kilbane
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django import template
from streampunk.models import Item, Person, Room, Tag
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
  return '<a href="/streampunk/%s/%d/%s/%d/">%s</a>' % (pname, pid, name, id, escape(value))

@register.simple_tag
def colheader(title, var, val):
  if var == val:
    return title
  else:
    return '<a href="" class="Show%s">%s</a>' % (val, title)

