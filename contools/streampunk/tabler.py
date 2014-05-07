# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2013-2014 Stephen Kilbane
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
  "Class for generating Tables2 table instances, with some local customisation."
  
  def __init__(self, tclass, rower, paginate=False, empty_text='(Nothing found)'):
    """
    Initial configuration of the table. tclass is a table. rower is a method on the model
    class that will return rows for the table. empty_text tells us what we use if there's
    nothing in the table. paginate is not currently used.
    """

    # Store each of the parameters for now.
    self.rower = rower
    self.tclass = tclass
    self.paginate = paginate
    self.empty_text = empty_text

  def table(self, qs, request=None, prefix=None, exclude=None):
    """
    Create the table instance using QuerySet qs for the table data. Request is the
    client's request, if any. Prefix can be used to distinguish multiple tables on the
    same page, if required. Exclude can be used to indicate columns that should not
    appear, for this instance of the table.
    """
    min_for_count = 6
    data = [ self.rower.row(thing) for thing in qs ]
    template = 'streampunk/table.html' if len(data) < min_for_count else None
    t = self.tclass(data, prefix=prefix, template=template, exclude=exclude, empty_text=self.empty_text)
    if request:
      config = RequestConfig(request, paginate={'per_page': len(data)})
      config.configure(t)
    else:
      t.paginate(page=1, per_page=len(data))
    return t

def make_tabler(mcls, tcls, request, qs, prefix=None, empty=None, extra_exclude=[]):
  rower = mcls.rower(request)
  exclude = mcls.tabler_exclude(request)
  exclude = extra_exclude if exclude == None else exclude + extra_exclude
  tbl = Tabler(tcls, rower, empty_text=empty)
  return tbl.table(qs, request=request, prefix=prefix, exclude=exclude)
