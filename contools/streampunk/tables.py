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

class ItemTable(tables.Table):
  select = tables.CheckBoxColumn(verbose_name='Select', accessor='id', attrs= select_attrs('itemtable') )
  shortname = tables.LinkColumn('show_item_detail', args=[A('pk')])
  title = tables.LinkColumn('show_item_detail', args=[A('pk')])
  edit = tables.TemplateColumn(EDITTEMPLATE % ('edit_item'), orderable=False)
  room = tables.LinkColumn('show_room_detail', args=[A('room.pk')])

  class Meta:
    model = Item
    fields = ( 'select', 'day', 'start', 'room', 'shortname', 'title', 'edit')
    attrs = { "class": "paleblue", "id": "sel_all" }


class PersonTable(tables.Table):
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

