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
    # Add a couple of standard attributes to the record that aren't
    # part of the table, but are used to drive the rendering of the
    # Edit/Remove fields. If the object doesn't include methods for
    # determining that, then default to saying 'yes', okay. Note
    # that permissions are checked separately.
    try:
      r['okay_to_edit'] = thing.okay_to_edit()
    except AttributeError:
      r['okay_to_edit'] = True
    try:
      r['okay_to_delete'] = thing.okay_to_delete()
    except AttributeError:
      r['okay_to_delete'] = True
    return r


class Tabler:
  def __init__(self, tclass, rower, paginate=False, empty_text='(Nothing found)'):
    self.rower = rower
    self.tclass = tclass
    self.paginate = paginate
    self.empty_text = empty_text

  def table(self, qs, request=None, prefix=None, exclude=None):
    template = 'streampunk/table.html'
    data = [ self.rower.row(thing) for thing in qs ]
    t = self.tclass(data, prefix=prefix, template=template, exclude=exclude, empty_text=self.empty_text)
    if request:
      config = RequestConfig(request)
      config.configure(t)
    return t

def make_tabler(mcls, tcls, request, qs, prefix=None, empty=None, extra_exclude=[]):
  rower = mcls.rower(request)
  exclude = mcls.tabler_exclude(request)
  exclude = extra_exclude if exclude == None else exclude + extra_exclude
  tbl = Tabler(tcls, rower, empty_text=empty)
  return tbl.table(qs, request=request, prefix=prefix, exclude=exclude)
