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

EDITTEMPLATE = '''
  <a href="{%% url %s pk=record.pk %%}" class="tbl_icon edit">Edit</a>
'''

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

class OldItemTable(tables.Table):
  select = tables.CheckBoxColumn(verbose_name='Select', accessor='id', attrs= select_attrs('itemtable') )
  shortname = tables.LinkColumn('show_item_detail', args=[A('pk')])
  title = tables.LinkColumn('show_item_detail', args=[A('pk')])
  edit = tables.TemplateColumn(EDITTEMPLATE % ('edit_item'), orderable=False)
  room = tables.LinkColumn('show_room_detail', args=[A('room.pk')])

  class Meta:
    model = Item
    fields = ( 'select', 'day', 'start', 'room', 'shortname', 'title', 'edit')
    attrs = { "class": "paleblue", "id": "sel_all" }


class OldPersonTable(tables.Table):
  select = tables.CheckBoxColumn(verbose_name='Select', accessor='id', attrs= select_attrs('persontable') )
  firstName = tables.LinkColumn('show_person_detail', args=[A('pk')], verbose_name='First Name')
  middleName = tables.LinkColumn('show_person_detail', args=[A('pk')], verbose_name='Middle Name')
  lastName = tables.LinkColumn('show_person_detail', args=[A('pk')], verbose_name='Last Name')
  name = tables.LinkColumn('show_person_detail', args=[A('pk')], accessor='as_name', orderable=False)
  badge = tables.LinkColumn('show_person_detail', args=[A('pk')])
  edit = tables.TemplateColumn(EDITTEMPLATE % ('edit_person'), orderable=False)
  class Meta:
    model = Person
    fields = ( 'select', 'firstName', 'middleName', 'lastName', 'name', 'badge', 'edit')
    attrs = { "class": "paleblue", "id": "sel_tbl" }

class PersonTable(tables.Table):
  select = tables.CheckBoxColumn(verbose_name='Select', accessor='pk', attrs= select_attrs('persontable') )
  name = tables.LinkColumn('show_person_detail', args=[A('pk')])
  email = tables.EmailColumn()
  edit = tables.LinkColumn('edit_person', args=[A('pk')])
  class Meta:
    attrs = { "class": "paleblue", "id": "sel_tbl" }

class RoomTable(tables.Table):
  name = tables.LinkColumn('show_room_detail', args=[A('pk')])
  grid = tables.Column()
  class Meta:
    attrs = { "class": "paleblue", "id": "sel_tbl" }

class ItemTable(tables.Table):
  day = tables.Column(order_by=[A('day.date')])
  time = tables.Column(order_by=[A('time.start')])
  room = tables.LinkColumn('show_room_detail', args=[A('pk')], order_by=[A('room.name')])
  shortname = tables.Column()
  title = tables.LinkColumn('show_item_detail', args=[A('pk')])
  edit = tables.LinkColumn('edit_item', args=[A('pk')])
  remove = tables.Column()
  class Meta:
    attrs = { "class": "paleblue", "id": "sel_tbl" }
