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

class EditColumn(tables.LinkColumn):
  def render(self, value, record, bound_column):
    if record['okay_to_edit']:
      return super(EditColumn, self).render(value=value, record=record, bound_column=bound_column)
    else:
      return '-'

class RemoveColumn(tables.LinkColumn):
  def render(self, value, record, bound_column):
    if record['okay_to_delete']:
      return super(RemoveColumn, self).render(value=value, record=record, bound_column=bound_column)
    else:
      return '-'

class PersonTable(tables.Table):
  select = tables.CheckBoxColumn(verbose_name='Select', accessor='pk', attrs= select_attrs('persontable') )
  memnum = tables.Column()
  name = tables.LinkColumn('show_person_detail', args=[A('pk')])
  firstName = tables.LinkColumn('show_person_detail', args=[A('pk')])
  middleName = tables.LinkColumn('show_person_detail', args=[A('pk')])
  lastName = tables.LinkColumn('show_person_detail', args=[A('pk')])
  badge = tables.LinkColumn('show_person_detail', args=[A('pk')])
  email = tables.EmailColumn()
  item_count = tables.Column()
  edit = EditColumn('edit_person', args=[A('pk')])
  remove = RemoveColumn('delete_person', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue", "id": "sel_tbl" }

class RoomTable(tables.Table):
  name = tables.LinkColumn('show_room_detail', args=[A('pk')])
  gridOrder = tables.Column(verbose_name='Grid Order')
  visible = tables.BooleanColumn()
  isDefault = tables.BooleanColumn(verbose_name='Default?')
  isUndefined = tables.BooleanColumn(verbose_name='Undef?')
  canClash = tables.BooleanColumn(verbose_name='Clash?')
  parent = tables.LinkColumn('show_room_detail', args=[A('parent.id')])
  description = tables.Column()
  privNotes = tables.Column()
  needsSound = tables.BooleanColumn(verbose_name='Sound?')
  naturalLight = tables.BooleanColumn(verbose_name='NatLight?')
  securable = tables.BooleanColumn(verbose_name='Secure?')
  controlLightsInRoom = tables.BooleanColumn(verbose_name='Lights?')
  controlAirConInRoom = tables.BooleanColumn(verbose_name='AirCon?')
  accessibleOnFlat = tables.BooleanColumn(verbose_name='Flat?')
  hasWifi = tables.BooleanColumn(verbose_name='Wifi?')
  hasCableRuns = tables.BooleanColumn(verbose_name='CblRuns?')
  openableWindows = tables.BooleanColumn(verbose_name='OpnWnds?')
  closableCurtains = tables.BooleanColumn(verbose_name='Curtains?')
  inRadioRange = tables.BooleanColumn(verbose_name='Radio?')
  techNotes = tables.Column(verbose_name='Tech Notes')

  edit = EditColumn('edit_room', args=[A('pk')])
  remove = RemoveColumn('delete_room', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }

class ItemTable(tables.Table):
  start = tables.Column(order_by=[A('start.start')])
  room = tables.LinkColumn('show_room_detail', args=[A('room.id')], order_by=[A('room.name')])
  title = tables.LinkColumn('show_item_detail', args=[A('pk')])
  shortname = tables.Column()
  projNeeded = tables.Column(verbose_name='Proj?')
  satisfies_kit_requests = tables.BooleanColumn(verbose_name='Kit OK?')
  edit = EditColumn('edit_item', args=[A('pk')])
  remove = RemoveColumn('delete_item', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }

class ItemKindTable(tables.Table):
  kind = tables.Column(verbose_name='Item Kind')
  count = tables.Column(verbose_name='Number of Items')
  class Meta:
    attrs = { "class": "paleblue" }

class GenderTable(tables.Table):
  gender = tables.Column()
  count = tables.Column()
  class Meta:
    attrs = { "class": "paleblue" }

class TagTable(tables.Table):
  name = tables.LinkColumn('show_tag_detail', args=[A('pk')])
  description = tables.Column()
  visible = tables.BooleanColumn()
  edit = EditColumn('edit_tag', args=[A('pk')])
  remove = RemoveColumn('delete_tag', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }

class KitThingTable(tables.Table):
  name = tables.LinkColumn('show_kitthing_detail', args=[A('pk')])
  kind = tables.Column(order_by=[A('kind.name')])
  count = tables.Column()
  notes = tables.Column()
  edit = EditColumn('edit_kitthing', args=[A('pk')])
  remove = RemoveColumn('delete_kitthing', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }
  
class KitRequestTable(tables.Table):
  name = tables.LinkColumn('show_kitrequest_detail', args=[A('pk')])
  kind = tables.Column(order_by=[A('kind.name')])
  count = tables.Column()
  status = tables.Column()
  setup = tables.Column()
  notes = tables.Column()
  item = tables.LinkColumn('show_item_detail', args=[A('item.pk')], verbose_name='Requested by')
  room = tables.LinkColumn('show_room_detail', args=[A('room.pk')])
  start = tables.Column()
  edit = EditColumn('edit_kitrequest', args=[A('pk')])
  remove = RemoveColumn('delete_kitrequest', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }

class KitRoomAssignmentTable(tables.Table):
  thing = tables.LinkColumn('show_kitthing_detail', args=[A('thing.id')])
  room = tables.LinkColumn('show_room_detail', args=[A('room.id')])
  bundle = tables.LinkColumn('show_kitbundle_detail', args=[A('bundle.id')])
  fromSlot = tables.Column()
  toSlot = tables.Column()
  remove = RemoveColumn('delete_kitroomassignment', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }

class KitItemAssignmentTable(tables.Table):
  thing = tables.LinkColumn('show_kitthing_detail', args=[A('thing.id')])
  item = tables.LinkColumn('show_item_detail', args=[A('item.id')])
  bundle = tables.LinkColumn('show_kitbundle_detail', args=[A('bundle.id')])
  room = tables.LinkColumn('show_room_detail', args=[A('room.id')])
  time = tables.Column()
  remove = RemoveColumn('delete_kititemassignment', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }

class ItemPersonTable(tables.Table):
  select = tables.CheckBoxColumn(verbose_name='Select', accessor='person.id', attrs= select_attrs('itempersontable') )
  item = tables.LinkColumn('show_item_detail', args=[A('item.id')])
  person = tables.LinkColumn('show_person_detail', args=[A('person.id')])
  role = tables.Column(order_by=[A('role.name')])
  status = tables.Column(order_by=[A('status.name')])
  visible = tables.BooleanColumn()
  distEmail = tables.Column(verbose_name='share email addr?')
  recordingOkay = tables.Column(verbose_name='Record item?')
  edit = EditColumn('edit_itemperson', args=[A('pk')])
  remove = RemoveColumn('delete_itemperson', args=[A('pk')])
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
  remove = RemoveColumn('delete_kitbundle', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }

class RoomCapacityTable(tables.Table):
  layout = tables.Column()
  count = tables.Column()
  class Meta:
    attrs = { "class": "paleblue" }

class AvailabilityTable(tables.Table):
  label = tables.Column()
  fromWhen = tables.DateTimeColumn(verbose_name='From')
  toWhen = tables.DateTimeColumn(verbose_name='To')

class PersonAvailabilityTable(AvailabilityTable):
  class Meta:
    attrs = { "class": "paleblue" }
class RoomAvailabilityTable(AvailabilityTable):
  class Meta:
    attrs = { "class": "paleblue" }
class KitAvailabilityTable(AvailabilityTable):
  class Meta:
    attrs = { "class": "paleblue" }

class GridTable(tables.Table):
  name = tables.LinkColumn('show_grid', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue" }
