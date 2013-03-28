# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2013 Stephen Kilbane
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

"""
Tabler for Streampunk, to convert querysets into Tables.
"""

from django_tables2 import RequestConfig

class Rower:
  def __init__(self, hash):
    self.hash = hash

  def row(self, thing):
    r = {}

    for k in self.hash.keys():
      v = self.hash[k]
      if callable(v):
        # method call
        r[k] = v(thing)
      else:
        try:
          # fetch named attribute
          r[k] = getattr(thing, v)
        except AttributeError:
          # Treat this as a dict, and do a key lookup
          try:
            r[k] = thing[v]
          except (AttributeError, TypeError):
            # use the string as a literal
            r[k] = v
    return r


class Tabler:
  def __init__(self, tclass, rower, paginate=False, empty_text='(Nothing found)'):
    self.rower = rower
    self.tclass = tclass
    self.paginate = paginate

  def table(self, qs, request=None, prefix=None, exclude=None):
    template = 'streampunk/table.html'
    data = [ self.rower.row(thing) for thing in qs ]
    t = self.tclass(data, prefix=prefix, template=template, exclude=exclude)
    if request:
      config = RequestConfig(request)
      config.configure(t)
    return t

