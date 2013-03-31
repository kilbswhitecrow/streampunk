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
Tables for Streampunk, to support sortable displays of data.
"""

import django_tables2 as tables
from django_tables2 import A
from models import Item, Person
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape

def select_attrs(tbl):
  "Set up the table with some attributes to use JQuery to toggle all the selection fields in in the table, if the header selection is clicked."
  th_attrs = {
    'class': '%s_hdr' % (tbl),
    'id': '%s_hdr' % (tbl),
    'onclick': 'toggle_checkboxes(this.id, "%s_one")' % (tbl)
  }
  td_attrs = {'class': '%s_one' % (tbl)}
  attrs = {
    'th__input': th_attrs,
    'td__input': td_attrs
  }
  return attrs

class PersonTable(tables.Table):
  select = tables.CheckBoxColumn(verbose_name='Select', accessor='pk', attrs= select_attrs('persontable') )
  name = tables.LinkColumn('show_person_detail', args=[A('pk')])
  firstName = tables.LinkColumn('show_person_detail', args=[A('pk')])
  middleName = tables.LinkColumn('show_person_detail', args=[A('pk')])
  lastName = tables.LinkColumn('show_person_detail', args=[A('pk')])
  badge = tables.LinkColumn('show_person_detail', args=[A('pk')])
  email = tables.EmailColumn()
  edit = tables.LinkColumn('edit_person', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue", "id": "sel_tbl" }

class RoomTable(tables.Table):
  name = tables.LinkColumn('show_room_detail', args=[A('pk')])
  grid = tables.Column()
  class Meta:
    attrs = { "class": "paleblue" }

class ItemTable(tables.Table):
  day = tables.Column(order_by=[A('day.date')])
  time = tables.Column(order_by=[A('time.start')])
  room = tables.LinkColumn('show_room_detail', args=[A('pk')], order_by=[A('room.name')])
  title = tables.LinkColumn('show_item_detail', args=[A('pk')])
  shortname = tables.Column()
  edit = tables.LinkColumn('edit_item', args=[A('pk')])
  remove = tables.Column()
  class Meta:
    attrs = { "class": "paleblue" }

class ItemKindTable(tables.Table):
  kind = tables.Column(verbose_name='Item Kind')
  count = tables.Column(verbose_name='Number of Items')
  class Meta:
    attrs = { "class": "paleblue" }

class TagTable(tables.Table):
  name = tables.LinkColumn('show_tag_detail', args=[A('pk')])
  description = tables.Column()
  visible = tables.BooleanColumn()
  edit = tables.LinkColumn('edit_tag', args=[A('pk')])
  remove = tables.Column()
  class Meta:
    attrs = { "class": "paleblue" }

class KitThingTable(tables.Table):
  name = tables.LinkColumn('show_kitthing_detail', args=[A('pk')])
  kind = tables.Column(order_by=[A('kind.name')])
  count = tables.Column()
  notes = tables.Column()
  remove = tables.LinkColumn('delete_kitthing', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }
  
class KitRequestTable(tables.Table):
  name = tables.LinkColumn('show_kitrequest_detail', args=[A('pk')])
  kind = tables.Column(order_by=[A('kind.name')])
  count = tables.Column()
  item = tables.LinkColumn('show_item_detail', args=[A('item.pk')], verbose_name='Requested by')
  room = tables.LinkColumn('show_room_detail', args=[A('room.pk')])
  day = tables.Column()
  start = tables.Column()
  sat = tables.Column(verbose_name='Satisfied by?')
  class Meta:
    attrs = { "class": "paleblue" }

class KitRoomAssignmentTable(tables.Table):
  thing = tables.LinkColumn('show_kitthing_detail', args=[A('pk')])
  room = tables.LinkColumn('show_room_detail', args=[A('pk')])
  bundle = tables.LinkColumn('show_kitbundle_detail', args=[A('pk')])
  fromday = tables.Column()
  fromtime = tables.Column()
  today = tables.Column()
  totime = tables.Column()
  remove = tables.LinkColumn('delete_kitroomassignment', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }

class KitItemAssignmentTable(tables.Table):
  thing = tables.LinkColumn('show_kitthing_detail', args=[A('pk')])
  item = tables.LinkColumn('show_item_detail', args=[A('pk')])
  bundle = tables.LinkColumn('show_kitbundle_detail', args=[A('pk')])
  room = tables.LinkColumn('show_room_detail', args=[A('pk')])
  day = tables.Column()
  time = tables.Column()
  remove = tables.LinkColumn('delete_kititemassignment', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }

class ItemPersonTable(tables.Table):
  select = tables.CheckBoxColumn(verbose_name='Select', accessor='person.id', attrs= select_attrs('itempersontable') )
  item = tables.LinkColumn('show_item_detail', args=[A('item.id')])
  person = tables.LinkColumn('show_person_detail', args=[A('person.id')])
  role = tables.Column(order_by=[A('role.name')])
  status = tables.Column(order_by=[A('status.name')])
  visible = tables.BooleanColumn()
  distEmail = tables.BooleanColumn(verbose_name='share email addr?')
  recordingOkay = tables.BooleanColumn(verbose_name='Record item?')
  edit = tables.LinkColumn('edit_itemperson', args=[A('pk')])
  remove = tables.LinkColumn('delete_itemperson', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue", "id": "ipt_tbl" }

class ListColumn(tables.Column):
  def render(self, value):
    if (len(value)):
      return mark_safe(reduce((lambda x, y: x+'<br />'+y),
                              map((lambda z: '<a href="%s">%s</a>' % (z.get_absolute_url(), escape(str(z)))), value)))
    else:
      return ''

class KitBundleTable(tables.Table):
  name = tables.LinkColumn('show_kitbundle_detail', args=[A('pk')])
  status = tables.Column()
  things = ListColumn(orderable=False)
  rooms = ListColumn(orderable=False)
  # If we call 'used_by' "items", rendering breaks. Can't figure out why
  used_by = ListColumn(orderable=False, verbose_name='Used by')
  remove = tables.LinkColumn('delete_kitbundle', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }
