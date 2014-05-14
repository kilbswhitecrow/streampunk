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
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.html import escape

from .models import Grid, Gender, Slot, SlotLength, Room
from .models import SlotLength, ConDay, ConInfoBool, ConInfoInt, ConInfoString
from .models import ItemKind, SeatingKind, FrontLayoutKind
from .models import Revision, MediaStatus, ItemPerson, Tag
from .models import PersonStatus, PersonRole, Person, Item
from .models import KitThing, KitRequest, KitBundle, KitRole, KitDepartment
from .models import KitKind, KitStatus, RoomCapacity, KitSource, KitBasis
from .models import KitRoomAssignment, KitItemAssignment
from .models import Check, CheckResult
from .exceptions import DeleteNeededObjectException, DeleteUndefException, DeleteDefaultException
from .testutils import itemdict, persondict, kitreqdict, kitthingdict, kitbundledict
from .testutils import default_person, default_item, default_itemperson
from .testutils import default_kitthing, default_kitbundle, default_kitrequest
from .testutils import item_lists_req, req_lists_item
from .testutils import item_lists_tag, tag_lists_item
from .testutils import person_lists_tags, item_lists_thing, thing_lists_item
from .testutils import room_lists_item, room_lists_thing
from .testutils import usage_lists_req_for_item, usage_lists_thing_for_item, usage_lists_bundle_for_item
from .testutils import usage_lists_thing_for_room, usage_lists_bundle_for_room
from .testutils import bundle_lists_thing, thing_lists_bundle
from .testutils import bundle_lists_item, thing_lists_item, item_lists_bundle
from .testutils import check_lists_item


class StreampunkTest(TestCase):

  def contextEqual(self, key, value):
    self.assertEqual(self.response.context[key], value)
  def contextNotEqual(key, value):
    self.assertNotEqual(self.response.context[key], value)

  def status_okay(self):
    self.assertEqual(self.response.status_code, 200)

  def has_link_to(self, path, args=None):
    link = '<a href="%s' % reverse(path, args=args)
    self.assertTrue(link in self.response.content)

  def no_link_to(self, path, args=None):
    link = '<a href="%s' % reverse(path, args=args)
    self.assertFalse(link in self.response.content)

  def form_error(self):
    self.assertTrue('errorlist' in self.response.content)

  def form_okay(self):
    self.assertFalse('errorlist' in self.response.content)

  def has_column(self, table, column):
    t = self.response.context[table]
    self.assertTrue(column in t.columns.names())

  def no_column(self, table, column):
    t = self.response.context[table]
    self.assertFalse(column in t.columns.names())

  def num_rows(self, table):
    t = self.response.context[table]
    return len(t.rows)

  def find_row(self, table, rec):
    "Locate a row which matches field/val pairs from rec, and return it"

    # Warning: a row has a record, and it has items(). The record is what
    # we pass to the Tables2 when we create the table, so will contain
    # our data, as converted into a dict by make_tabler(). The result of
    # items() will be the rendered cell content, including links.
    # We might be providing strings, or objects that render to strings, or
    # callables that provide objects or strings, so we need to try each of
    # these dereferences before giving up.
    # Note also that the keys in the record dict need not match the titles
    # of the columns.

    def rec_val(thing):
      return thing() if callable(thing) else thing
    t = self.response.context[table]
    for row in t.rows:
      if rec <= row.record:
        # all of rec' keys appear in the row's record. Now get a list of
        # all the keys where the values are different. If this list is
        # empty, then this row matches the rec.
        diffs = [ k for k in rec.keys() if not k in row.record or str(rec[k]) != str(rec_val(row.record[k])) ]
        if not diffs:
          return row.record
    return None

  def row_match(self, table, rec):
    "Test whether table has a row which matches the field/value pairs from dict rec."
    row = self.find_row(table, rec)
    return True if row else False

  def has_row(self, table, rec):
    self.assertTrue(self.row_match(table, rec))

  def no_row(self, table, rec):
    self.assertFalse(self.row_match(table, rec))

  def get_buffy(self):
    return Person.objects.get(firstName='Buffy')
  def get_giles(self):
    return Person.objects.get(lastName='Giles')
  def get_willow(self):
    return Person.objects.get(firstName='Willow')
  def get_dawn(self):
    return Person.objects.get(firstName='Dawn')
  def get_xander(self):
    return Person.objects.get(firstName='Alexander')

  def get_ceilidh(self):
    return Item.objects.get(shortname='Ceilidh')
  def get_disco(self):
    return Item.objects.get(shortname='Disco')
  def get_cabaret(self):
    return Item.objects.get(shortname='Masquerade')
  def get_bidsession(self):
    return Item.objects.get(shortname='bid session')

  def get_nowhere(self):
    return Room.objects.get(name='Nowhere')
  def get_everywhere(self):
    return Room.objects.get(name='Everywhere')
  def get_video(self):
    return Room.objects.get(name='Video')
  def get_ops(self):
    return Room.objects.get(name='Ops')
  def get_mainhall(self):
    return Room.objects.get(name='Main Hall')

  def get_proj(self):
    return KitKind.objects.get(name='Projector')
  def get_screen(self):
    return KitKind.objects.get(name='Screen')

  def get_greenroomproj(self):
    return KitThing.objects.get(name='Green room projector')
  def get_greenroomscr(self):
    return KitThing.objects.get(name='Green room screen')
  def get_mainhallkit(self):
    return KitBundle.objects.get(name='Main hall kit')
  def get_mainhallproj(self):
    return  KitThing.objects.get(name='Main hall projector')
  def get_mainhallscr(self):
    return KitThing.objects.get(name='Main hall screen')

  def get_friday(self):
    return ConDay.objects.get(name='Friday')
  def get_saturday(self):
    return ConDay.objects.get(name='Saturday')
  def get_sunday(self):
    return ConDay.objects.get(name='Sunday')
  def get_monday(self):
    return ConDay.objects.get(name='Monday')
  def get_morning(self):
    friday = self.get_friday()
    return Slot.objects.get(day=friday, startText='10am')
  def get_evening(self):
    sunday = self.get_sunday()
    return Slot.objects.get(day=sunday, startText='8pm')
  def get_hour(self):
    return SlotLength.objects.get(length=60)

  def get_books(self):
    return Tag.objects.get(name='Books')
  def get_movies(self):
    return Tag.objects.get(name='Movies')
  def get_comics(self):
    return Tag.objects.get(name='Comics')

  def get_panellist(self):
    return PersonRole.objects.get(name='Panellist')
  def get_panel(self):
    return ItemKind.objects.get(name='Panel')

  def get_theatre(self):
    return SeatingKind.objects.get(name='Theatre')
  def get_empty(self):
    return SeatingKind.objects.get(name='Empty')

class NonauthTest(StreampunkTest):

  def banner(self):
    self.has_link_to('login')
    self.no_link_to('logout')
    self.has_link_to('list_grids')
    self.has_link_to('list_people')
    self.has_link_to('list_rooms')
    self.has_link_to('list_items')
    self.has_link_to('list_tags')

    for g in Grid.objects.all():
      self.has_link_to('show_grid', args=(int(g.id),))

class AuthTest(StreampunkTest):

  def banner(self):
    self.no_link_to('login')
    self.has_link_to('logout')
    self.has_link_to('list_grids')
    self.has_link_to('list_people')
    self.has_link_to('list_rooms')
    self.has_link_to('list_rooms_prog')
    self.has_link_to('list_rooms_tech')
    self.has_link_to('list_items')
    self.has_link_to('list_tags')
    self.has_link_to('new_person')
    self.has_link_to('new_item')
    self.has_link_to('new_room')
    self.has_link_to('new_tag')
    self.has_link_to('add_tags')
    self.has_link_to('list_kitbundles')
    self.has_link_to('list_kitthings')
    self.has_link_to('kit_usage')
    self.has_link_to('list_checks')
    # To Add
    # kit thing/bundle to room/item
    # admin
    # Profile

  def mkroot(self):
    user = User.objects.create_user(username='congod', password='xxx')
    user.is_superuser = True
    user.save()
    self.rootuser = user

  def zaproot(self):
    self.rootuser.delete()


# =========================================================


class nonauth_lists(NonauthTest):
  def setUp(self):
    self.client = Client()

  def test_main_page0(self):
    "No items or people yet. Not logged in."
    self.response = self.client.get(reverse('main_page'))
    self.status_okay()
    self.contextEqual('con_name', u'MyCon 2012')
    self.contextEqual('num_items', 0)
    self.contextEqual('num_people', 0)
    self.contextEqual('num_panellists', 0)
    self.contextEqual('budget', 0)
    self.contextEqual('hours_scheduled', 0)
    self.banner()
    self.has_link_to('xml_dump')
    self.no_link_to('new_itemperson')
    self.no_link_to('add_tags')
    self.no_link_to('make_con_groups')
    self.has_column('kind_table', 'kind')
    self.has_column('kind_table', 'count')

  def test_items0(self):
    "No items yet, but there should be a table"
    t = 'itable'
    self.response = self.client.get(reverse('list_items'))
    self.status_okay()
    self.has_column(t, 'title')
    self.has_column(t, 'room')
    self.has_column(t, 'start')
    self.assertEqual(self.num_rows(t), 0)
    self.no_link_to('new_item')

  def test_people0(self):
    "No people yet, but there should be a table"
    t = 'ptable'
    self.response = self.client.get(reverse('list_people'))
    self.status_okay()
    self.has_column(t, 'name')
    self.has_column(t, 'badge')
    self.no_column(t, 'memnum')
    self.assertEqual(self.num_rows(t), 0)
    self.no_link_to('new_person')


  def test_rooms0(self):
    "We should have Nowhere and Everywhere, but only the latter is visible."
    t = 'rtable'
    self.response = self.client.get(reverse('list_rooms'))
    self.status_okay()
    self.has_column(t, 'name')
    self.has_column(t, 'gridOrder')
    self.has_column(t, 'description')
    self.assertEqual(self.num_rows(t), 1)
    self.no_row(t, { 'name': 'Nowhere' })
    self.has_row(t, { 'name': 'Everywhere' })
    self.no_link_to('new_room')

  def test_tags0(self):
    "No tags yet, but there should be a table"
    t = 'ttable'
    self.response = self.client.get(reverse('list_tags'))
    self.status_okay()
    self.has_column(t, 'name')
    self.has_column(t, 'description')
    self.assertEqual(self.num_rows(t), 0)
    self.no_link_to('new_tag')


# =========================================================


class Auth_lists(AuthTest):
  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_login(self):
    self.assertTrue(self.logged_in_okay)

  def test_main_page1(self):
    "No items or people yet. Now logged in."
    self.response = self.client.get(reverse('main_page'))
    self.status_okay()
    self.contextEqual('con_name', u'MyCon 2012')
    self.contextEqual('num_items', 0)
    self.contextEqual('num_people', 0)
    self.contextEqual('num_panellists', 0)
    self.contextEqual('budget', 0)
    self.contextEqual('hours_scheduled', 0)
    self.banner()
    self.has_link_to('xml_dump')
    self.has_link_to('new_itemperson')
    self.has_link_to('add_tags')
    self.has_link_to('make_con_groups')
    self.has_column('kind_table', 'kind')
    self.has_column('kind_table', 'count')

  def test_items1(self):
    "No items yet, but check we can see all columns"
    t = 'itable'
    self.response = self.client.get(reverse('list_items'))
    self.status_okay()
    self.has_column(t, 'title')
    self.has_column(t, 'room')
    self.has_column(t, 'start')
    self.has_column(t, 'shortname')
    self.has_column(t, 'edit')
    self.has_column(t, 'remove')
    self.assertEqual(self.num_rows(t), 0)
    self.has_link_to('new_item')

  def test_people1(self):
    "No people yet, but there should be a table"
    t = 'ptable'
    self.response = self.client.get(reverse('list_people'))
    self.status_okay()
    self.no_column(t, 'name')
    self.has_column(t, 'firstName')
    self.has_column(t, 'middleName')
    self.has_column(t, 'lastName')
    self.has_column(t, 'badge')
    self.has_column(t, 'memnum')
    self.has_column(t, 'email')
    self.has_column(t, 'edit')
    self.has_column(t, 'remove')
    self.assertEqual(self.num_rows(t), 0)
    self.has_link_to('new_person')
    # Need a way to test that there a submit buttons for forms, too.


  def test_rooms1(self):
    "We should have Nowhere and Everywhere, and be able to see both."
    t = 'rtable'
    self.response = self.client.get(reverse('list_rooms'))
    self.status_okay()
    self.has_column(t, 'name')
    self.has_column(t, 'gridOrder')
    self.has_column(t, 'description')
    self.has_column(t, 'visible')
    self.has_column(t, 'edit')
    self.has_column(t, 'remove')
    self.assertEqual(self.num_rows(t), 2)
    self.has_row(t, { 'name': 'Nowhere', 'visible': False, 'edit': 'Edit', 'remove': 'Remove' })
    self.has_row(t, { 'name': 'Everywhere', 'visible': True, 'edit': 'Edit', 'remove': 'Remove' })
    self.has_link_to('new_room')

  def test_tags1(self):
    "No tags yet, but there should be a table"
    t = 'ttable'
    self.response = self.client.get(reverse('list_tags'))
    self.status_okay()
    self.has_column(t, 'name')
    self.has_column(t, 'description')
    self.has_column(t, 'visible')
    self.has_column(t, 'edit')
    self.has_column(t, 'remove')
    self.assertEqual(self.num_rows(t), 0)
    self.has_link_to('new_tag')
    self.has_link_to('add_tags')


# =========================================================


class test_creation(AuthTest):
  "Populate the tables somewhat"

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_mkpeople(self):
    def chkpeople(self, numrows):
      t = 'ptable'
      self.response = self.client.get(reverse('list_people'))
      self.status_okay()
      self.no_column(t, 'name')
      self.has_column(t, 'firstName')
      self.has_column(t, 'middleName')
      self.has_column(t, 'lastName')
      self.has_column(t, 'badge')
      self.has_column(t, 'memnum')
      self.has_column(t, 'email')
      self.has_column(t, 'edit')
      self.has_column(t, 'remove')
      self.assertEqual(self.num_rows(t), numrows)
      self.has_link_to('new_person')

    t = 'ptable'
    chkpeople(self, 0)
    self.response = self.client.post(reverse('new_person'), default_person({
      "firstName":      "Rupert",
      "lastName":       "Giles",
      "badge":          "Ripper"
    }), follow=True)
    self.status_okay()
    chkpeople(self, 1)
    self.has_row(t, { 'firstName': 'Rupert', 'lastName': 'Giles', 'edit': 'Edit', 'remove': 'Remove' })

    self.response = self.client.post(reverse('new_person'), default_person({
      "firstName":      "Buffy",
      "lastName":       "Summers"
    }), follow=True)
    self.status_okay()
    chkpeople(self, 2)
    self.has_row(t, { 'firstName': 'Rupert', 'lastName': 'Giles', 'edit': 'Edit', 'remove': 'Remove' })
    self.has_row(t, { 'firstName': 'Buffy', 'lastName': 'Summers', 'edit': 'Edit', 'remove': 'Remove' })

  def test_mkrooms(self):
    def chkroom(self, numrows):
      t = 'rtable'
      self.response = self.client.get(reverse('list_rooms'))
      self.status_okay()
      self.has_column(t, 'name')
      self.has_column(t, 'gridOrder')
      self.has_column(t, 'description')
      self.has_column(t, 'visible')
      self.has_column(t, 'edit')
      self.has_column(t, 'remove')
      self.assertEqual(self.num_rows(t), numrows)
      self.has_row(t, { 'name': 'Nowhere', 'visible': False, 'edit': 'Edit', 'remove': 'Remove' })
      self.has_row(t, { 'name': 'Everywhere', 'visible': True, 'edit': 'Edit', 'remove': 'Remove' })
      self.has_link_to('new_room')

    t = 'rtable'
    chkroom(self, 2)
    self.response = self.client.post(reverse('new_room'), {
      "name":        "Main Hall",
      "isDefault":   False,
      "isUndefined": False,
      "canClash":    False,
      "visible":     True,
      "gridOrder":   10
    }, follow=True)
    self.status_okay()
    chkroom(self, 3)
    self.has_row(t, { 'name': 'Main Hall', 'visible': True, 'edit': 'Edit', 'remove': 'Remove' })

    self.response = self.client.post(reverse('new_room'), {
      "name":        "Ops",
      "isDefault":   False,
      "isUndefined": False,
      "canClash":    False,
      "gridOrder":   20
    }, follow=True)
    self.status_okay()
    chkroom(self, 4)
    self.has_row(t, { 'name': 'Main Hall', 'visible': True,  'edit': 'Edit', 'remove': 'Remove' })
    self.has_row(t, { 'name': 'Ops',       'visible': False, 'edit': 'Edit', 'remove': 'Remove' })

  def test_mkitems(self):
    def chkitems(self, numrows):
      t = 'itable'
      self.response = self.client.get(reverse('list_items'))
      self.status_okay()
      self.has_column(t, 'title')
      self.has_column(t, 'room')
      self.has_column(t, 'start')
      self.has_column(t, 'shortname')
      self.has_column(t, 'edit')
      self.has_column(t, 'remove')
      self.assertEqual(self.num_rows(t), numrows)
      self.has_link_to('new_item')

    t = 'itable'
    chkitems(self, 0)
    self.response = self.client.post(reverse('new_item'), default_item({
      "title":       "Opening Ceremony",
      "shortname":   "opening ceremony",
      }), follow=True)
    self.status_okay()
    chkitems(self, 1)
    self.has_row(t, { 'title': 'Opening Ceremony', 'edit': 'Edit', 'remove': 'Remove' })

    self.response = self.client.post(reverse('new_item'), default_item({
      "title":     "Bid Session",
      "shortname": "bid"
      }), follow=True)
    self.status_okay()
    chkitems(self, 2)
    self.has_row(t, { 'title': 'Opening Ceremony', 'edit': 'Edit', 'remove': 'Remove' })
    self.has_row(t, { 'title': 'Bid Session', 'edit': 'Edit', 'remove': 'Remove' })

  def test_mktags(self):
    def chktags(self, numrows):
      t = 'ttable'
      self.response = self.client.get(reverse('list_tags'))
      self.status_okay()
      self.has_column(t, 'name')
      self.has_column(t, 'description')
      self.has_column(t, 'visible')
      self.has_column(t, 'edit')
      self.has_column(t, 'remove')
      self.assertEqual(self.num_rows(t), numrows)
      self.has_link_to('new_tag')
      self.has_link_to('add_tags')

    t = 'ttable'
    chktags(self, 0)
    self.response = self.client.post(reverse('new_tag'), {
      "name": "books",
      "visible": True
    }, follow=True)
    self.status_okay()
    chktags(self, 1)
    self.has_row(t, { 'name': 'books', 'visible': True, 'edit': 'Edit', 'remove': 'Remove' })

    self.response = self.client.post(reverse('new_tag'), {
      "name": "movies"
    }, follow=True)
    self.status_okay()
    chktags(self, 2)
    self.has_row(t, { 'name': 'books', 'visible': True, 'edit': 'Edit', 'remove': 'Remove' })
    self.has_row(t, { 'name': 'movies', 'visible': False, 'edit': 'Edit', 'remove': 'Remove' })

  def test_mkkitthings(self):
    self.response = self.client.post(reverse('new_kitthing'), {
      "name": "Main Hall Projector"
    })
    self.status_okay()

    self.response = self.client.post(reverse('new_kitthing'), {
      "name": "Main Hall Screen"
    })
    self.status_okay()



# =========================================================


class test_add_panellists(AuthTest):
  "Adding people to items."
  fixtures = [ 'room', 'person', 'items', 'tags', 'kit' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_people_items(self):
    buffy = self.get_buffy()
    giles = self.get_giles()
    ceilidh = self.get_ceilidh()
    disco = self.get_disco()
    panellist = PersonRole.objects.find_default()
    
    itable = 'item_people_table'  # people on the item
    ptable = 'person_items_table' # items person is on

    # Add Buffy to an item

    self.response = self.client.post(reverse('new_itemperson'), default_itemperson({
      "item":    disco.id,
      "person":  buffy.id,
      "role":    panellist.id
    }), follow=True)
    self.status_okay()

    self.response = self.client.get(reverse('show_person_detail', kwargs={ "pk": buffy.id }))
    self.status_okay()
    self.assertEqual(self.num_rows(ptable), 1)
    self.has_row(ptable, { "item": disco, "role": panellist })

    self.response = self.client.get(reverse('show_item_detail', kwargs={ "pk": disco.id }))
    self.status_okay()
    self.has_row(itable, { "person": buffy, "role": panellist, "visible": True })

    # Add Giles to an item

    self.response = self.client.post(reverse('new_itemperson'), default_itemperson({
      "item":    ceilidh.id,
      "person":  giles.id,
      "role":    panellist.id
    }), follow=True)
    self.status_okay()

    self.response = self.client.get(reverse('show_person_detail', kwargs={ "pk": giles.id }))
    self.status_okay()
    self.has_row(ptable, { "item": ceilidh, "role": panellist, "visible": True })

    self.response = self.client.get(reverse('show_item_detail', kwargs={ "pk": ceilidh.id }))
    self.status_okay()
    self.has_row(itable, { "person": giles, "role": panellist, "visible": True })

    # Add Buffy to another item

    self.response = self.client.post(reverse('new_itemperson'), default_itemperson({
      "item":    ceilidh.id,
      "person":  buffy.id,
      "role":    panellist.id
    }), follow=True)
    self.status_okay()

    # Add Giles to another item

    self.response = self.client.post(reverse('new_itemperson'), default_itemperson({
      "item":    disco.id,
      "person":  giles.id,
      "role":    panellist.id
    }), follow=True)
    self.status_okay()

    self.response = self.client.get(reverse('show_person_detail', kwargs={ "pk": buffy.id }))
    self.status_okay()
    self.assertEqual(self.num_rows(ptable), 2)
    self.has_row(ptable, { "item": ceilidh, "role": panellist })
    self.has_row(ptable, { "item": disco, "role": panellist })

    self.response = self.client.get(reverse('show_item_detail', kwargs={ "pk": ceilidh.id }))
    self.status_okay()
    self.assertEqual(self.num_rows(itable), 2)
    self.has_row(itable, { "person": buffy, "role": panellist, "visible": True })
    self.has_row(itable, { "person": giles, "role": panellist, "visible": True })

    self.response = self.client.get(reverse('show_person_detail', kwargs={ "pk": giles.id }))
    self.status_okay()
    self.assertEqual(self.num_rows(ptable), 2)
    self.has_row(ptable, { "item": disco, "role": panellist, "visible": True })
    self.has_row(ptable, { "item": ceilidh, "role": panellist, "visible": True })

    self.response = self.client.get(reverse('show_item_detail', kwargs={ "pk": disco.id }))
    self.status_okay()
    self.assertEqual(self.num_rows(itable), 2)
    self.has_row(itable, { "person": giles, "role": panellist, "visible": True })
    self.has_row(itable, { "person": buffy, "role": panellist, "visible": True })

    # Add Giles to the same item

    self.response = self.client.post(reverse('new_itemperson'), default_itemperson({
      "item":    disco.id,
      "person":  giles.id,
      "role":    panellist.id
    }), follow=True)
    self.status_okay()

    # Giles shouldn't be on that item twice.

    self.assertFormError(self.response, 'form', field=None,
                         errors='Itemperson with this Item and Person already exists.')

    # Find where Buffy is on the Disco item
    ip = ItemPerson.objects.get(person=buffy, item=disco)

    # Try deleting with a GET, check Buffy's still there.
    self.response = self.client.get(reverse('delete_itemperson', kwargs={ "pk": ip.id }))
    self.status_okay()
    self.response = self.client.get(reverse('show_item_detail', kwargs={ "pk": disco.id }))
    self.status_okay()
    self.assertEqual(self.num_rows(itable), 2)
    self.has_row(itable, { "person": buffy, "role": panellist, "visible": True })
    
    # But a POST should work.
    self.response = self.client.post(reverse('delete_itemperson', kwargs={ "pk": ip.id }), {
      "after": reverse('show_item_detail', kwargs={ "pk": disco.id })
    },  follow=True)
    self.status_okay()
    self.response = self.client.get(reverse('show_item_detail', kwargs={ "pk": disco.id }))
    self.status_okay()
    self.assertEqual(self.num_rows(itable), 1)
    self.no_row(itable, { "person": buffy, "role": panellist, "visible": True })
    self.response = self.client.get(reverse('show_person_detail', kwargs={ "pk": buffy.id }))
    self.status_okay()
    self.assertEqual(self.num_rows(ptable), 1)
    self.no_row(ptable, { "item": disco, "role": panellist, "visible": True })

  def test_edit_person(self):
    buffy = self.get_buffy()
    eaddr = 'buffy@sunnydale.net'
    self.response = self.client.get(reverse('edit_person', kwargs={ "pk": buffy.id }))
    self.status_okay()
    object = self.response.context['object']
    postdata = persondict(object)
    postdata['email'] = eaddr
    self.response = self.client.post(reverse('edit_person', kwargs={ "pk": buffy.id }), postdata, follow=True)
    self.status_okay()
    person = self.response.context['person']
    self.assertEqual(buffy.id, person.id)
    self.assertEqual(eaddr, person.email)
    buf2 = Person.objects.get(email=eaddr)
    self.assertEqual(buffy.id, buf2.id)

  def test_person_tags(self):

    def tagids(tagqs):
      return [ t.id for t in tagqs ]

    buffy = self.get_buffy()
    giles = self.get_giles()
    books = self.get_books()
    movies = self.get_movies()

    # No tags for anyone yet
    person_lists_tags(self, buffy, [])
    person_lists_tags(self, giles, [])
    self.response = self.client.get(reverse('edit_tags_for_person', args=[ buffy.id ]))
    self.status_okay()

    fperson = self.response.context['person']

    # Create a new set of tags, that has a couple more
    newtags = [ t for t in fperson.tags.all() ] + [ books, movies ]
    self.response = self.client.post(reverse('edit_tags_for_person', args=[ buffy.id ]), {
      "tags": tagids(newtags)
    }, follow=True)
    self.status_okay()
    person_lists_tags(self, buffy, newtags)
    person_lists_tags(self, giles, [])

    # Again, but with only one new tag.
    # Looks like this particular test currently fails.
    newtags = [ books ]
    self.response = self.client.post(reverse('edit_tags_for_person', args=[ buffy.id ]), {
      "tags": tagids(newtags)
    }, follow=True)
    self.status_okay()
    person_lists_tags(self, buffy, newtags)
    person_lists_tags(self, giles, [])

    # If we include tags twice, they should not get added twice.
    newtags = [ books, movies ]
    toomanytags = newtags + [ books, movies ]
    self.response = self.client.post(reverse('edit_tags_for_person', args=[ buffy.id ]), {
      "tags": tagids(toomanytags)
    }, follow=True)
    self.status_okay()
    person_lists_tags(self, buffy, newtags)
    person_lists_tags(self, giles, [])

    # Check the person shows up under the tags page, too.
    self.response = self.client.get(reverse('show_tag_detail', kwargs={'pk': books.id}))
    self.status_okay()
    t = 'pttable'
    self.assertEqual(self.num_rows(t), 1)
    self.has_row(t, { 'firstName': buffy.firstName })

    self.response = self.client.get(reverse('show_tag_detail', kwargs={'pk': movies.id}))
    self.status_okay()
    t = 'pttable'
    self.assertEqual(self.num_rows(t), 1)
    self.has_row(t, { 'firstName': buffy.firstName })

# =========================================================


class test_delete_people(AuthTest):
  "Deleting people"
  fixtures = [ 'room', 'person', 'items', 'tags', 'kit' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_people_items(self):
    buffy = self.get_buffy()
    willow = self.get_willow()
    dawn = self.get_dawn()
    disco = self.get_disco()
    ceilidh = self.get_ceilidh()
    books = self.get_books()
    movies = self.get_movies()
    panellist = self.get_panellist()

    # Deleting via a GET should not remove the person
    delpath = reverse('delete_person', kwargs={'pk': buffy.id})
    self.response = self.client.get(delpath)
    self.status_okay()
    self.assertTrue(Person.objects.filter(firstName='Buffy').exists())

    # Deleting via a POST should, however.
    self.response = self.client.post(delpath, { }, follow=True)
    self.status_okay()
    self.assertFalse(Person.objects.filter(firstName='Buffy').exists())

    # Check that it's okay to delete a person who is on some items.
    # First, add a couple of tags.
    delpath = reverse('delete_person', kwargs={'pk': willow.id})
    self.response = self.client.post(reverse('edit_tags_for_person', args=[ willow.id ]), {
      "tags": ( books.id, movies.id )
    }, follow=True)
    self.status_okay()
    self.assertEqual(willow.tags.count(), 2)
    # Now check that we can delete them.
    self.response = self.client.post(delpath, { }, follow=True)
    self.status_okay()
    self.assertFalse(Person.objects.filter(firstName='Willow').exists())

    # Check that it's okay to delete a person who is on some items
    # First, add Dawn to a couple of items.

    delpath = reverse('delete_person', kwargs={'pk': dawn.id})
    self.response = self.client.post(reverse('new_itemperson'), default_itemperson({
      "item":    disco.id,
      "person":  dawn.id,
      "role":    panellist.id
    }), follow=True)
    self.status_okay()

    self.response = self.client.post(reverse('new_itemperson'), default_itemperson({
      "item":    ceilidh.id,
      "person":  dawn.id,
      "role":    panellist.id
    }), follow=True)
    self.status_okay()
    self.assertEqual(ItemPerson.objects.filter(person=dawn).count(), 2)

    # Now try deleting them.
    self.response = self.client.post(delpath, { }, follow=True)
    self.status_okay()
    self.assertFalse(Person.objects.filter(firstName='Dawn').exists())

# =========================================================

class test_delete_items_with_stuff(AuthTest):
  "Deleting items"
  fixtures = [ 'room', 'person', 'items', 'tags', 'kit' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_items_people_tags(self):
    "Test deleting items, with people and tags."
  
    buffy = self.get_buffy()
    willow = self.get_willow()
    dawn = self.get_disco()
    disco = self.get_disco()
    ceilidh = self.get_ceilidh()
    bid = self.get_bidsession()
    books = self.get_books()
    movies = self.get_movies()
    panellist = self.get_panellist()

    # Deleting via a GET should not remove the item
    delpath = reverse('delete_item', kwargs={'pk': bid.id})
    self.response = self.client.get(delpath)
    self.status_okay()
    self.assertTrue(Item.objects.filter(shortname='bid session').exists())

    # Deleting via a POST should, however.
    self.response = self.client.post(delpath, { }, follow=True)
    self.status_okay()
    self.assertFalse(Item.objects.filter(shortname='bid session').exists())

    # Check that it's okay to delete an item that has some tags
    # First, add a couple of tags.
    delpath = reverse('delete_item', kwargs={'pk': disco.id})
    self.response = self.client.post(reverse('edit_tags_for_item', args=[ disco.id ]), {
      "tags": ( books.id, movies.id )
    }, follow=True)
    self.status_okay()
    self.assertEqual(disco.tags.count(), 2)
    # Now check that we can delete them.
    self.response = self.client.post(delpath, { }, follow=True)
    self.status_okay()
    self.assertFalse(Item.objects.filter(shortname='Disco').exists())

    # Check that it's okay to delete an item that has people on it.
    # First, add some people

    delpath = reverse('delete_item', kwargs={'pk': ceilidh.id})
    self.response = self.client.post(reverse('new_itemperson'), default_itemperson({
      "item":    ceilidh.id,
      "person":  dawn.id,
      "role":    panellist.id
    }), follow=True)
    self.status_okay()

    self.response = self.client.post(reverse('new_itemperson'), default_itemperson({
      "item":    ceilidh.id,
      "person":  buffy.id,
      "role":    panellist.id
    }), follow=True)
    self.status_okay()
    self.assertEqual(ItemPerson.objects.filter(item=ceilidh).count(), 2)

    # Now try deleting them.
    self.response = self.client.post(delpath, { }, follow=True)
    self.status_okay()
    self.assertFalse(Item.objects.filter(shortname='Ceilidh').exists())

  def test_items_kit(self):
    disco = self.get_disco()
    ceilidh = self.get_ceilidh()
    bid = self.get_bidsession()
    mhproj = self.get_mainhallproj()
    mhscreen = self.get_mainhallscr()
    mhkit = self.get_mainhallkit()

    self.assertEqual(KitRequest.objects.count(), 0)
    self.assertEqual(KitItemAssignment.objects.count(), 0)

    # Add a kit request to some items
    self.response = self.client.post(reverse('add_kitrequest_to_item', args=[ disco.id ]), {
      "kind": KitKind.objects.find_default().id,
      "count": 1,
      "setupAssistance": False,
      "status": KitStatus.objects.find_default().id
    }, follow=True)
    self.status_okay()
    self.assertEqual(KitRequest.objects.count(), 1)

    self.response = self.client.post(reverse('add_kitrequest_to_item', args=[ ceilidh.id ]), {
      "kind": KitKind.objects.find_default().id,
      "count": 1,
      "setupAssistance": False,
      "status": KitStatus.objects.find_default().id
    }, follow=True)
    self.status_okay()
    self.assertEqual(KitRequest.objects.count(), 2)

    # Add KitThings to an item
    self.response = self.client.post(reverse('add_kitthing_to_item'), {
      "item": ceilidh.id,
      "thing": mhproj.id
    }, follow=True)
    self.status_okay()
    self.assertEqual(KitItemAssignment.objects.count(), 1)

    self.response = self.client.post(reverse('add_kitbundle_to_item'), {
      "item": bid.id,
      "bundle": mhkit.id
    }, follow=True)
    self.status_okay()
    self.assertEqual(KitItemAssignment.objects.count(), 1+mhkit.things.count())

    # Check that we can delete those items now.
    delpath = reverse('delete_item', kwargs={'pk': disco.id})
    self.response = self.client.post(delpath, { }, follow=True)
    self.status_okay()
    self.assertFalse(Item.objects.filter(shortname='Disco').exists())
    # The request should be gone now.
    self.assertEqual(KitRequest.objects.count(), 1)

    delpath = reverse('delete_item', kwargs={'pk': ceilidh.id})
    self.response = self.client.post(delpath, { }, follow=True)
    self.status_okay()
    self.assertFalse(Item.objects.filter(shortname='Ceilidh').exists())
    # The other request should be gone now.
    self.assertEqual(KitRequest.objects.count(), 0)
    # The KitItemAssignment should have gone now.
    self.assertEqual(KitItemAssignment.objects.count(), mhkit.things.count())

    delpath = reverse('delete_item', kwargs={'pk': bid.id})
    self.response = self.client.post(delpath, { }, follow=True)
    self.status_okay()
    self.assertFalse(Item.objects.filter(shortname='bid session').exists())
    # All assignments should be gone now.
    self.assertEqual(KitItemAssignment.objects.count(), 0)

# =========================================================

class test_delete_tags(AuthTest):
  "Deleting tags"
  fixtures = [ 'room', 'person', 'items', 'tags' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_delete_tags_on_stuff(self):
    "Test deleting tags, on people and items."
    buffy = self.get_buffy()
    disco = self.get_disco()
    books = self.get_books()
    movies = self.get_movies()
    comics = self.get_comics()

    # Add tag to an item
    self.response = self.client.post(reverse('edit_tags_for_item', args=[ disco.id ]), {
      "tags": ( books.id )
    }, follow=True)
    self.status_okay()
    # Add tag to a person
    self.response = self.client.post(reverse('edit_tags_for_person', args=[ buffy.id ]), {
      "tags": ( movies.id )
    }, follow=True)
    self.status_okay()

    # Establish that we've set things up properly.
    self.assertEqual(books.item_set.count(), 1)
    self.assertEqual(books.person_set.count(), 0)
    self.assertEqual(movies.item_set.count(), 0)
    self.assertEqual(movies.person_set.count(), 1)
    self.assertEqual(comics.item_set.count(), 0)
    self.assertEqual(comics.person_set.count(), 0)
    self.assertTrue(buffy in movies.person_set.all())
    self.assertTrue(disco in books.item_set.all())
    self.assertEqual(buffy.tags.count(), 1)
    self.assertEqual(disco.tags.count(), 1)
    self.assertTrue(books in disco.tags.all())
    self.assertTrue(movies in buffy.tags.all())

    # Deleting via GET shouldn't work.
    self.response = self.client.get(reverse('delete_tag', args=[ comics.id ]))
    self.status_okay()
    self.assertTrue(Tag.objects.filter(name='Comics').exists())

    # Deleting via POST should.
    self.response = self.client.post(reverse('delete_tag', args=[ comics.id ]), { }, follow=True)
    self.status_okay()
    self.assertFalse(Tag.objects.filter(name='Comics').exists())

    # And we should be able to delete a tag that's on a person...
    self.response = self.client.post(reverse('delete_tag', args=[ movies.id ]), { }, follow=True)
    self.status_okay()
    self.assertFalse(Tag.objects.filter(name='Movies').exists())

    # And we should be able to delete a tag that's on an item...
    self.response = self.client.post(reverse('delete_tag', args=[ books.id ]), { }, follow=True)
    self.status_okay()
    self.assertFalse(Tag.objects.filter(name='Books').exists())

    # Which should leave the person and item tag-bereft.
    self.assertEqual(buffy.tags.count(), 0)
    self.assertEqual(disco.tags.count(), 0)

# =========================================================

class test_delete_rooms(AuthTest):
  "Deleting rooms"
  fixtures = [ 'room', 'items', 'kit' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_delete_rooms_with_stuff(self):
    "Test deleting rooms, with items and capacities."
    disco = self.get_disco()
    video = self.get_video()
    ops = self.get_ops()
    nowhere = self.get_nowhere()
    mainhall = self.get_mainhall()

    # No items in Ops.
    self.assertEqual(ops.item_set.count(), 0)

    # deleting via GET should fail.
    self.response = self.client.get(reverse('delete_room', args=[ ops.id ]))
    self.status_okay()
    self.assertTrue(Room.objects.filter(name='Ops').exists())

    # deleting via POST should work
    self.response = self.client.post(reverse('delete_room', args=[ ops.id ]), { }, follow=True)
    self.status_okay()
    self.assertFalse(Room.objects.filter(name='Ops').exists())

    # Lots of items in the main hall
    self.assertEqual(mainhall.item_set.count(), 7)
    mh_item_ids = [ i.id for i in mainhall.item_set.all() ]

    # we can delete the Main Hall
    self.response = self.client.post(reverse('delete_room', args=[ mainhall.id ]), { }, follow=True)
    self.status_okay()
    self.assertFalse(Room.objects.filter(name='Main Hall').exists())

    # But all those items should still exist, now in Nowhere
    for i in mh_item_ids:
      self.assertTrue(Item.objects.filter(id=i, room=nowhere).exists())

    # We should get an assertion if we try to delete nowhere, though.
    with self.assertRaises(DeleteNeededObjectException):
      self.client.post(reverse('delete_room', args=[ nowhere.id ]), { })
    self.assertTrue(Room.objects.filter(name='Nowhere').exists())

    # We don't currently have a GUI for adding capacities, so that has
    # to be done through the Admin interface. Therefore, we'll just create
    # some directly now.

    theatre = self.get_theatre()
    empty = self.get_empty()
    cap1 = RoomCapacity(layout=theatre, count=60)
    cap1.save()
    cap2 = RoomCapacity(layout=empty, count=300)
    cap2.save()

    cap1id = cap1.id
    cap2id = cap2.id

    # check our counts: two capacity objects, none of which are
    # attached to a room yet.
    self.assertEqual(RoomCapacity.objects.count(), 2)
    self.assertEqual(video.capacities.count(), 0)

    # Attach cap1 to the Video room, but leave cap2 unattached.
    video.capacities.add(cap1)
    video.save()

    self.assertEqual(video.capacities.count(), 1)
    self.assertEqual(cap1.room_set.count(), 1)
    self.assertEqual(cap2.room_set.count(), 0)

    # Delete the Video room.
    self.response = self.client.post(reverse('delete_room', args=[ video.id ]), { }, follow=True)
    self.status_okay()

    self.assertFalse(Room.objects.filter(name='Video').exists())

    # Currently, we expect both capacity object to still exist, but
    # we go back to cap1 no longer having a room attached.
    self.assertEqual(RoomCapacity.objects.count(), 2)

    self.assertTrue(RoomCapacity.objects.filter(id=cap1id).exists())
    cap1 = RoomCapacity.objects.get(id=cap1id)
    self.assertEqual(cap1.room_set.count(), 0)

    self.assertTrue(RoomCapacity.objects.filter(id=cap2id).exists())
    cap2 = RoomCapacity.objects.get(id=cap2id)
    self.assertEqual(cap2.room_set.count(), 0)

  def test_delete_rooms_with_kit(self):
    "Test deleting rooms, with kit items and kit bundles."
    video = self.get_video()
    ops = self.get_ops()
    mainhall = self.get_mainhall()

    greenproj = self.get_greenroomproj()
    greenscr = self.get_greenroomscr()
    mainhallkit = self.get_mainhallkit()
    mhcount = mainhallkit.things.count()

    friday = self.get_friday()
    sunday = self.get_sunday()
    morning = self.get_morning()
    evening = self.get_evening()
    hour = self.get_hour()

    # Nothing assigned to any rooms yet.
    self.assertEqual(KitRoomAssignment.objects.count(), 0)

    # Add the green room kit to Ops
    for kt in [ greenproj, greenscr ]:
      self.response = self.client.post(reverse('add_kitthing_to_room'), {
        "room": ops.id,
        "thing": kt.id,
        "fromSlot": morning.id,
        "toSlot": evening.id,
        "toLength": hour.id
      }, follow=True)
      self.status_okay()
    self.assertEqual(KitRoomAssignment.objects.count(), 2)
    self.assertEqual(greenproj.room_set.count(), 1)
    self.assertEqual(greenproj.room_set.count(), 1)

    # Add the Main Hall bundle to the main hall
    self.response = self.client.post(reverse('add_kitbundle_to_room'), {
      "room": mainhall.id,
      "bundle": mainhallkit.id,
      "fromSlot": morning.id,
      "toSlot": evening.id,
      "toLength": hour.id
     }, follow=True)
    self.status_okay()
    self.assertEqual(KitRoomAssignment.objects.count(), mhcount+2)
    for kt in mainhallkit.things.all():
      self.assertEqual(kt.room_set.count(), 1)
    self.assertEqual(KitRoomAssignment.objects.filter(bundle=mainhallkit).count(), mhcount)

    # Now delete the main hall.
    self.response = self.client.post(reverse('delete_room', args=[ mainhall.id ]), {}, follow=True)
    self.status_okay()
 
    # The room should have gone.
    self.assertFalse(Room.objects.filter(name='Main Hall').exists())
 
    # The KitRoomAssignments for the main hall should have gone.
    self.assertEqual(KitRoomAssignment.objects.count(), 2)
    self.assertEqual(KitRoomAssignment.objects.filter(bundle=mainhallkit).count(), 0)
    self.assertEqual(KitRoomAssignment.objects.filter(room=ops).count(), 2)
 
    # but the bundle should stil be there.
    self.assertTrue(KitBundle.objects.filter(name='Main hall kit').exists())
    mainhallkit = self.get_mainhallkit()
    # with all its kit
    self.assertEqual(mainhallkit.things.count(), mhcount)
 
    # Now zap Ops
    self.response = self.client.post(reverse('delete_room', args=[ ops.id ]), {}, follow=True)
    self.status_okay()
 
    # The other assignments should be gone, now.
    self.assertEqual(KitRoomAssignment.objects.count(), 0)
    # Our Things should still be there.
    self.assertTrue(KitThing.objects.filter(name='Green room projector').exists())
    self.assertTrue(KitThing.objects.filter(name='Green room screen').exists())
# =========================================================

class test_delete_enums(AuthTest):
  "Deleting enumerations and other important things."
  fixtures = [ 'room', 'person', 'items', 'kit' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  # Each enum type has a delete method, so that if something has value X,
  # and you delete X from the enum, it correctly changes that something to
  # use value Y for the enum, instead.

  def poke_enum(self, all, should_change, change_from, change_to, matches):
    for i in all:
      if i in should_change:
        self.assertTrue(matches(i, change_from))
        self.assertFalse(matches(i, change_to))
      else:
        self.assertFalse(matches(i, change_from))
    change_from.delete()
    for i in all:
      if i in should_change:
        # Refetch the thing from the database
        j = i.__class__.objects.get(id=i.id)
        self.assertTrue(matches(j, change_to))

  def test_delete_needed_objects(self):
    "Test deleting things that should not be deleted."

    disco = self.get_disco()
    ikdefault = ItemKind.objects.get(isDefault=True)
    ikundef = ItemKind.objects.get(isUndefined=True)
    ikdisco = disco.kind
    ikid = ikdisco.id
    self.assertNotEqual(ikdefault, ikdisco)

    # EnumTables don't have streampunk URLs for deleting - it's done
    # through the admin interface, so let's just zap things directly.

    ikdisco.delete()
    self.assertFalse(ItemKind.objects.filter(id=ikid).exists())

    # And anything that used the now-removed enum should be
    # using its undef value instead
    disco = self.get_disco()
    self.assertEqual(ikundef, disco.kind)

    # Trying to delete the undefined kind should raise an exception
    with self.assertRaises(DeleteNeededObjectException):
      ikundef.delete()
    self.assertEqual(ItemKind.objects.filter(isUndefined=True).count(), 1)

    # Trying to delete the default kind should raise an exception
    with self.assertRaises(DeleteNeededObjectException):
      ikdefault.delete()
    self.assertEqual(ItemKind.objects.filter(isDefault=True).count(), 1)

  def test_delete_undef(self):
    "move the undef flag to somewhere else, and then check which exceptions we get."

    ikdefault = ItemKind.objects.find_default()
    ikpanel = self.get_panel()
    ikdefault.isDefault = False
    ikdefault.save()
    ikpanel.isDefault = True
    ikpanel.save()
    ikdefault = ItemKind.objects.find_default()
    ikundef = ItemKind.objects.find_undefined()

    self.assertNotEqual(ikdefault, ikundef)

    # Now if we try to delete ikundef, we should get DeleteUndefException,
    # because it's not the default

    with self.assertRaises(DeleteUndefException):
      ikundef.delete()

  def test_delete_default(self):
    "move the default flag to somewhere else, and then check which exceptions we get."

    ikundef = ItemKind.objects.find_undefined()
    ikpanel = self.get_panel()
    ikundef.isUndefined = False
    ikundef.save()
    ikpanel.isUndefined = True
    ikpanel.save()
    ikdefault = ItemKind.objects.find_default()
    ikundef = ItemKind.objects.find_undefined()

    self.assertNotEqual(ikdefault, ikundef)

    # Now if we try to delete ikdefault, we should get DeleteDefaultException,
    # because it's not undefined.

    with self.assertRaises(DeleteDefaultException):
      ikdefault.delete()

  def test_delete_methods_seating(self):
    "Prod each enum type's delete() method."


    # SeatingKind
    # TBA: None
    # Theatre: bid, closing, interview, auction, etc.
    # Empty: ceilidh, disco
    self.poke_enum(all=Item.objects.all(),
                   should_change=Item.objects.filter(seating__name='Empty'),
                   change_from=SeatingKind.objects.get(name='Empty'),
                   change_to=SeatingKind.objects.find_undefined(),
                   matches=(lambda thing, val: thing.seating==val))

    
  def test_delete_methods_frontlayout(self):
    # FrontLayoutKind
    # TBA: nothing
    # Panel: everything

    # Since we've only got a single useful value, let's create another.
    lecture = FrontLayoutKind(name='Lecture')
    lecture.save()
    # Let's make sure it's used.
    should_change=Item.objects.filter(seating__name='Empty')
    should_change.update(frontLayout=lecture)

    # Then see what happens when we delete it.
    self.poke_enum(all=Item.objects.all(),
                   should_change=should_change,
                   change_from=lecture,
                   change_to=FrontLayoutKind.objects.find_undefined(),
                   matches=(lambda thing, val: thing.frontLayout==val))

  def test_delete_methods_mediastatus(self):
    # MediaStatus
    # Choice of 4, everything TBA, so change some to one value,
    # and others to another.
    none_req=MediaStatus.objects.get(name='No media required')
    recv=MediaStatus.objects.get(name='Media received by Tech')
    should_change=Item.objects.filter(seating__name='Empty')
    should_change.update(mediaStatus=none_req)
    Item.objects.exclude(seating__name='Empty').update(mediaStatus=recv)
    self.poke_enum(all=Item.objects.all(),
                   should_change=should_change,
                   change_from=none_req,
                   change_to=MediaStatus.objects.find_undefined(),
                   matches=(lambda thing, val: thing.mediaStatus==val))

  def test_delete_methods_itempeople(self):
    # Make sure we have some people on items.
    buffy = self.get_buffy()
    dawn = self.get_dawn()
    giles = self.get_giles()
    xander = self.get_xander()
    disco = self.get_disco()
    bid = self.get_bidsession()

    mod = PersonRole.objects.get(name='Moderator')
    speaker = PersonRole.objects.get(name='Speaker')
    panellist = self.get_panellist()

    invited = PersonStatus.objects.get(name='Invited')
    confirmed = PersonStatus.objects.get(name='Confirmed')

    # We'll delete Moderator, leave Speaker untouched.
    xanderbid = ItemPerson(item=bid, person=xander, role=mod, status=confirmed)
    gilesbid = ItemPerson(item=bid, person=giles, role=mod, status=confirmed)

    # We'll delete Proposed, and leave Confirmed untouched.
    buffydisco = ItemPerson(item=disco, person=buffy, role=speaker, status=invited)
    gilesdisco = ItemPerson(item=disco, person=giles, role=speaker, status=invited)
    dawndisco = ItemPerson(item=disco, person=dawn, role=speaker, status=invited)

    xanderbid.save()
    gilesbid.save()
    buffydisco.save()
    gilesdisco.save()
    dawndisco.save()

    # PersonRole
    # Choice of 4+, everything TBA

    self.poke_enum(all=ItemPerson.objects.all(),
                   should_change=[ gilesbid, xanderbid ],
                   change_from=mod,
                   change_to=PersonRole.objects.find_undefined(),
                   matches=(lambda thing, val: thing.role==val))

    # PersonStatus
    # Several choices, all TBA

    self.poke_enum(all=ItemPerson.objects.all(),
                   should_change=[ buffydisco, gilesdisco, dawndisco],
                   change_from=invited,
                   change_to=PersonStatus.objects.find_undefined(),
                   matches=(lambda thing, val: thing.status==val))

  def test_delete_methods_gender(self):
    # Gender
    # Male, Female, TBA, split 50/50

    self.poke_enum(all=Person.objects.all(),
                   should_change=Person.objects.filter(gender__name='Male'),
                   change_from=Gender.objects.get(name='Male'),
                   change_to=Gender.objects.find_undefined(),
                   matches=(lambda thing, val: thing.gender==val))

  def test_delete_methods_kitthings(self):
    # KitKind
    # Lots of choices, screens, projectors, mics
    # Different ones used

    self.poke_enum(all=KitThing.objects.all(),
                   should_change=KitThing.objects.filter(kind__name='Projector'),
                   change_from=KitKind.objects.get(name='Projector'),
                   change_to=KitKind.objects.find_undefined(),
                   matches=(lambda thing, val: thing.kind==val))

    # KitRole
    # only TBA

    # Create a couple of roles, and make sure they're used.
    apple=KitRole(name='Apple')
    pear=KitRole(name='Pear')
    apple.save()
    pear.save()

    # We also need to create some kit sources
    scotty=KitSource(name='Scotty')
    brains=KitSource(name='Brains')
    scotty.save()
    brains.save()

    mics = KitThing.objects.filter(kind__name='Microphone')
    screens = KitThing.objects.filter(kind__name='Screen')
    progops=KitDepartment.objects.get(name='Programme Ops')
    green=KitDepartment.objects.get(name='Green Room')
    borrow=KitBasis.objects.get(name='Borrow')
    buy=KitBasis.objects.get(name='Buy')
    purchase=KitStatus.objects.get(name='Awaiting purchase')
    delivered=KitStatus.objects.get(name='Delivered')

    mics.update(role=apple, department=progops, source=brains, basis=borrow, status=purchase)
    screens.update(role=pear, department=green, source=scotty, basis=buy, status=delivered)

    self.poke_enum(all=KitThing.objects.all(),
                   should_change=mics,
                   change_from=apple,
                   change_to=KitRole.objects.find_undefined(),
                   matches=(lambda thing, val: thing.role==val))

    # KitDepartment
    # several choices
    # Only one used, though

    self.poke_enum(all=KitThing.objects.all(),
                   should_change=mics,
                   change_from=progops,
                   change_to=KitDepartment.objects.find_undefined(),
                   matches=(lambda thing, val: thing.department==val))

    # KitSource
    # just TBA

    self.poke_enum(all=KitThing.objects.all(),
                   should_change=mics,
                   change_from=brains,
                   change_to=KitSource.objects.find_undefined(),
                   matches=(lambda thing, val: thing.source==val))

    # KitBasis
    # choice of four
    # All TBA

    self.poke_enum(all=KitThing.objects.all(),
                   should_change=mics,
                   change_from=borrow,
                   change_to=KitBasis.objects.find_undefined(),
                   matches=(lambda thing, val: thing.basis==val))

    # KitStatus
    # choice of 4 +
    # All TBA

    self.poke_enum(all=KitThing.objects.all(),
                   should_change=mics,
                   change_from=purchase,
                   change_to=KitStatus.objects.find_undefined(),
                   matches=(lambda thing, val: thing.status==val))

  def test_delete_methods_checkresult(self):
    # CheckResult
    # Choice of several, no TBA
    # All are used

    roomlist=CheckResult.objects.get(name='Room List')

    self.poke_enum(all=Check.objects.all(),
                   should_change=Check.objects.filter(result=roomlist),
                   change_from=roomlist,
                   change_to=CheckResult.objects.find_undefined(),
                   matches=(lambda thing, val: thing.result==val))

# =========================================================

class test_edit_items(AuthTest):
  "Editing aspects of an item."
  fixtures = [ 'room', 'items', 'tags', 'kit' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_item_edit_error(self):
    "Test that we can detect an error occurred in an item edit"

    disco = self.get_disco()
    self.response = self.client.post(reverse('edit_item', args=[disco.id]), { }, follow=True)
    self.form_error()

  def test_edit_basic_stuff(self):
    "Change some basic things about an item."

    disco = self.get_disco()
    mainhall = self.get_mainhall()
    ops = self.get_ops()
    hour = self.get_hour()
    panel = self.get_panel()

    self.assertEqual(mainhall, disco.room)
    room_lists_item(self, mainhall, disco, True)

    # Get a form for editing.
    editurl = reverse('edit_item', args=[ disco.id ])
    self.response = self.client.get(editurl)
    self.status_okay()

    # Fetch the item from the form presented
    i = self.response.context['object']

    self.assertEqual(i.shortname, disco.shortname)
    self.assertNotEqual(i.room, ops)
    self.assertNotEqual(i.length, hour)
    self.assertNotEqual(i.kind, panel)

    i = itemdict(i)
    i['room'] = ops.id
    i['length'] = hour.id
    i['kind'] = panel.id

    # Send the updated data back.
    self.response = self.client.post(editurl, i, follow=True)
    self.status_okay()
    self.form_okay()
    i = self.response.context['item']

    # Check it's been changed
    self.assertEqual(i.shortname, disco.shortname)
    self.assertEqual(i.room, ops)
    self.assertEqual(i.length, hour)
    self.assertEqual(i.kind, panel)

    disco = self.get_disco()
    mainhall = self.get_mainhall()
    ops = self.get_ops()
    room_lists_item(self, mainhall, disco, False)
    room_lists_item(self, ops, disco, True)

  def test_edit_item_tags(self):
    "Change the tags on an item."

    disco = self.get_disco()
    editurl = reverse('edit_tags_for_item', args=[ disco.id ])
    books = self.get_books()
    movies = self.get_movies()

    # Check that there's no tags on the item yet
    self.assertEqual(disco.tags.count(), 0)
    # Check that the tags aren't attached to any items
    self.assertEqual(books.item_set.count(), 0)
    self.assertEqual(movies.item_set.count(), 0)

    # Check that the item doesn't appear in a search on the tags
    tag_lists_item(self, books, disco, False)
    tag_lists_item(self, movies, disco, False)
    # And that the item doesn't list the tags
    item_lists_tag(self, disco, books, False)
    item_lists_tag(self, disco, movies, False)

    # Add one of the tags to the item.
    self.response = self.client.post(editurl, { "tags": [ books.id ] }, follow=True)
    self.status_okay()
    self.form_okay()

    # Check that the item now lists books, but not movies.
    tag_lists_item(self, books, disco, True)
    tag_lists_item(self, movies, disco, False)
    # And that the item lists only books
    item_lists_tag(self, disco, books, True)
    item_lists_tag(self, disco, movies, False)
    self.assertEqual(disco.tags.count(), 1)
    self.assertEqual(books.item_set.count(), 1)
    self.assertEqual(movies.item_set.count(), 0)

    # Add movies, too.
    self.response = self.client.post(editurl, { "tags": [ books.id, movies.id ] }, follow=True)
    self.status_okay()
    self.form_okay()

    # Check that the item now lists both books and movies.
    tag_lists_item(self, books, disco, True)
    tag_lists_item(self, movies, disco, True)
    # And that the item lists only books
    item_lists_tag(self, disco, books, True)
    item_lists_tag(self, disco, movies, True)
    self.assertEqual(disco.tags.count(), 2)
    self.assertEqual(books.item_set.count(), 1)
    self.assertEqual(movies.item_set.count(), 1)

    # Edit to remove books, and leave movies there.
    self.response = self.client.post(editurl, { "tags": [ movies.id ] }, follow=True)
    self.status_okay()
    self.form_okay()

    # Check that the item now lists movies, but not books.
    tag_lists_item(self, books, disco, False)
    tag_lists_item(self, movies, disco, True)
    # And that the item lists only books
    item_lists_tag(self, disco, books, False)
    item_lists_tag(self, disco, movies, True)
    self.assertEqual(disco.tags.count(), 1)
    self.assertEqual(books.item_set.count(), 0)
    self.assertEqual(movies.item_set.count(), 1)

    # Edit again, to have no tags.
    self.response = self.client.post(editurl, { }, follow=True)
    self.status_okay()
    self.form_okay()

    tag_lists_item(self, books, disco, False)
    tag_lists_item(self, movies, disco, False)
    # And that the item doesn't list the tags
    item_lists_tag(self, disco, books, False)
    item_lists_tag(self, disco, movies, False)
    self.assertEqual(disco.tags.count(), 0)
    self.assertEqual(books.item_set.count(), 0)
    self.assertEqual(movies.item_set.count(), 0)

    # Edit to include books twice; check that we don't get two instances.
    self.response = self.client.post(editurl, { "tags": [ books.id, books.id ] }, follow=True)
    self.status_okay()
    self.form_okay()

    tag_lists_item(self, books, disco, True)
    tag_lists_item(self, movies, disco, False)
    item_lists_tag(self, disco, books, True)
    item_lists_tag(self, disco, movies, False)
    self.assertEqual(disco.tags.count(), 1)
    self.assertEqual(books.item_set.count(), 1)
    self.assertEqual(movies.item_set.count(), 0)

  def test_edit_kit_requests(self):
    "Change kit requests on an item."

    disco = self.get_disco()

    # No kit requests yet.
    self.assertEqual(KitRequest.objects.count(), 0)

    self.response = self.client.post(reverse('add_kitrequest_to_item', args=[ disco.id ]), {
      "kind": KitKind.objects.find_default().id,
      "count": 1,
      "setupAssistance": False,
      "status": KitStatus.objects.find_default().id
    }, follow=True)
    self.status_okay()
    self.form_okay()
    self.assertEqual(KitRequest.objects.count(), 1)

    # Let's see which one it is.
    req = KitRequest.objects.all()[0]
    reqid = req.id

    # Make sure it's on the item, and vice versa
    item_lists_req(self, disco, req, True)
    # req_lists_item(self, req, disco, True)
    usage_lists_req_for_item(self, req, disco, True)
    disco = self.get_disco()
    self.assertTrue(req in disco.kitRequests.all())
    self.assertTrue(disco in req.item_set.all())
    self.assertEqual(req.count, 1)

    # Edit the item.
    newreq = kitreqdict(req)
    newreq['count'] = 3
    self.response = self.client.post(reverse('edit_kitrequest', args=[ req.id ]), newreq, follow=True)
    self.status_okay()
    self.form_okay()

    # fetch it again, then check it's still listed.
    req = KitRequest.objects.get(id = reqid)
    item_lists_req(self, disco, req, True)
    # req_lists_item(self, req, disco, True)
    usage_lists_req_for_item(self, req, disco, True)
    disco = self.get_disco()
    self.assertTrue(req in disco.kitRequests.all())
    self.assertTrue(disco in req.item_set.all())
    self.assertEqual(req.count, 3)

    # delete it.
    self.response = self.client.post(reverse('delete_kitrequest', args=[ req.id ]), { }, follow=True)
    self.status_okay()
    self.assertEqual(KitRequest.objects.count(), 0)

  def test_edit_kit_things(self):
    "Adding/removing/editing kit things on items and rooms."

    def thing_gone(self, thingname, item=None, room=None):
      self.response = self.client.get(reverse('list_kitthings'))
      self.status_okay()
      self.no_row('kttable', { "name": thingname })
      self.response = self.client.get(reverse('kit_usage'))
      self.status_okay()
      self.no_row('kiatable', { "name": thingname })
      if item:
        self.response = self.client.get(reverse('show_item_detail', args=[ item.id ]))
        self.status_okay()
        self.no_row('kiatable', { "name": thingname })
      if room:
        self.response = self.client.get(reverse('show_room_detail', args=[ room.id ]))
        self.status_okay()
        self.no_row('kratable', { "name": thingname })

    proj = self.get_proj()
    projname = "THX Projector"
    projname2 = "Dolby Projector"

    # Create a new thing
    self.response = self.client.post(reverse('new_kitthing'), default_kitthing({
      "name": projname,
      "kind": proj.id
    }), follow=True)
    self.status_okay()
    self.form_okay()

    # Fetch that new item
    thx = KitThing.objects.get(name=projname)
    self.assertEqual(thx.count, 1)

    # Should be listed with other kitthings.
    self.response = self.client.get(reverse('list_kitthings'))
    self.status_okay()
    self.has_row('kttable', { "name": projname, "count": 1 })

    # Should be able to modify it.
    editurl = reverse('edit_kitthing', args=[ thx.id ])
    self.response = self.client.get(editurl)
    self.status_okay()
    formobj = self.response.context['object']
    d = kitthingdict(formobj)
    d['name'] = projname2
    d['count'] = 42

    self.response = self.client.post(editurl, d, follow=True)
    self.status_okay()
    self.form_okay()

    # Is it now listed as changed?
    self.response = self.client.get(reverse('list_kitthings'))
    self.status_okay()
    self.no_row('kttable', { "name": projname })
    self.has_row('kttable', { "name" : projname2, "count": 42 } )

    # fetch it again
    thx = KitThing.objects.get(id=thx.id)

    # Add the thing to an item.

    disco = self.get_disco()
    item_lists_thing(self, disco, thx, False)
    self.response = self.client.post(reverse('add_kitthing_to_item'), {
      "thing": thx.id,
      "item": disco.id
    }, follow=True)
    self.status_okay()
    self.form_okay()

    item_lists_thing(self, disco, thx, True)
    thing_lists_item(self, thx, disco, True)
    usage_lists_thing_for_item(self, thx, disco, True)

    # Edit, while attached to the item.
    d['count'] = 16
    self.response = self.client.post(editurl, d, follow=True)
    self.status_okay()
    self.form_okay()
    item_lists_thing(self, disco, thx, True)
    thing_lists_item(self, thx, disco, True)
    usage_lists_thing_for_item(self, thx, disco, True)

    # Delete it again.
    self.response = self.client.post(reverse('delete_kitthing', args=[ thx.id ]), { }, follow=True)
    self.status_okay()

    # Should now be gone
    thing_gone(self, projname2, item=disco)

    # create it again
    self.response = self.client.post(reverse('new_kitthing'), default_kitthing({
      "name": projname,
      "kind": proj.id
    }), follow=True)
    self.status_okay()
    self.form_okay()

    # Fetch that new item
    thx = KitThing.objects.get(name=projname)
    self.assertEqual(thx.count, 1)

    # Not on a room yet
    mainhall = self.get_mainhall()
    room_lists_thing(self, mainhall, thx, False)
    usage_lists_thing_for_room(self, thx, mainhall, False)

    # Attach it to a room
    morning = self.get_morning()
    evening = self.get_evening()
    hour = self.get_hour()

    self.response = self.client.post(reverse('add_kitthing_to_room'), {
      "thing": thx.id,
      "room": mainhall.id,
      "fromSlot": morning.id,
      "toSlot": evening.id,
      "toLength": hour.id
    }, follow=True)
    self.status_okay()
    self.form_okay()

    # Now on the room
    room_lists_thing(self, mainhall, thx, True)
    usage_lists_thing_for_room(self, thx, mainhall, True)

    # Should be able to modify it.
    editurl = reverse('edit_kitthing', args=[ thx.id ])
    self.response = self.client.get(editurl)
    self.status_okay()
    formobj = self.response.context['object']
    d = kitthingdict(formobj)

    # Edit, while attached to the room.
    d['count'] = 666
    self.response = self.client.post(editurl, d, follow=True)
    self.status_okay()
    self.form_okay()

    # Fetch it again
    thx = KitThing.objects.get(id=thx.id)
    self.assertEqual(thx.count, 666)
    room_lists_thing(self, mainhall, thx, True)
    usage_lists_thing_for_room(self, thx, mainhall, True)

    # Delete it again.
    self.response = self.client.post(reverse('delete_kitthing', args=[ thx.id ]), { }, follow=True)
    self.status_okay()

    # Should now be gone
    thing_gone(self, projname, room=mainhall)

  def test_edit_kit_bundles(self):
    "Adding/removing/editing kit bundles on items and rooms."

    bname = 'Quiz Gear'
    proj = self.get_proj()
    projname = "THX Projector"
    scr = self.get_screen()
    scrname = "3D Screen"
    bid = self.get_bidsession()
    ops = self.get_ops()

    self.response = self.client.post(reverse('new_kitthing'), default_kitthing({
      "name": projname,
      "kind": proj.id
    }), follow=True)
    self.status_okay()
    self.form_okay()
    projector = KitThing.objects.get(name=projname)

    self.response = self.client.post(reverse('new_kitthing'), default_kitthing({
      "name": scrname,
      "kind": scr.id
    }), follow=True)
    self.status_okay()
    self.form_okay()
    screen = KitThing.objects.get(name=scrname)

    # Check that the bundle we want isn't listed yet
    self.response = self.client.post(reverse('list_kitbundles'), follow=True)
    self.status_okay()
    self.no_row('kbtable', { "name": bname })

    # Create a new bundle
    self.response = self.client.post(reverse('new_kitbundle'), default_kitbundle({
      "name": bname,
      "things": [ projector.id, screen.id ]
    }), follow=True)
    self.status_okay()
    self.form_okay()

    # Should now be listed
    self.response = self.client.post(reverse('list_kitbundles'), { }, follow=True)
    self.status_okay()
    self.has_row('kbtable', { "name": bname })

    # fetch it
    qb = KitBundle.objects.get(name=bname)
    bundle_lists_thing(self, qb, projector, True)
    thing_lists_bundle(self, projector, qb, True)
    bundle_lists_thing(self, qb, screen, True)
    thing_lists_bundle(self, screen, qb, True)

    editurl = reverse('edit_kitbundle', args=[ qb.id ])

    # Add the bundle to an item
    self.response = self.client.post(reverse('add_kitbundle_to_item'), {
      "bundle": qb.id,
      "item": bid.id
    }, follow=True)
    self.status_okay()
    self.form_okay()

    # And to a room
    morning = self.get_morning()
    evening = self.get_evening()
    hour = self.get_hour()

    self.response = self.client.post(reverse('add_kitbundle_to_room'), {
      "bundle": qb.id,
      "room": ops.id,
      "fromSlot": morning.id,
      "toSlot": evening.id,
      "toLength": hour.id
    }, follow=True)
    self.status_okay()
    self.form_okay()

   # Now everything should list everything
    item_lists_bundle(self, bid, qb, True)
    bundle_lists_item(self, qb, bid, True)
    usage_lists_bundle_for_item(self, qb, bid, True)
    usage_lists_bundle_for_room(self, qb, ops, True)
    bundle_lists_thing(self, qb, projector, True)
    thing_lists_bundle(self, projector, qb, True)
    bundle_lists_thing(self, qb, screen, True)
    thing_lists_bundle(self, screen, qb, True)

    # Remove the screen from the bundle, by setting the things to just the projector
    self.response = self.client.get(editurl)
    self.status_okay()
    formobj = self.response.context['object']
    d = kitbundledict(formobj)

    # Edit, while attached to the room.
    d['things'] = [ projector.id ]
    self.response = self.client.post(editurl, d, follow=True)
    self.status_okay()
    self.form_okay()
    bundle_lists_thing(self, qb, projector, True)
    thing_lists_bundle(self, projector, qb, True)
    bundle_lists_thing(self, qb, screen, False)
    thing_lists_bundle(self, screen, qb, False)

    # Delete it
    self.response = self.client.post(reverse('delete_kitbundle', args=[qb.id]), { }, follow=True)
    self.status_okay()

    # Check that the bundle isn't listed anymore
    self.response = self.client.post(reverse('list_kitbundles'), { }, follow=True)
    self.status_okay()
    self.no_row('kbtable', { "name": bname })

    # And the things no longer think they're in the bundle
    # XXX we may have a problem here, since qb will no longer be valid...
    thing_lists_bundle(self, projector, qb, False)
    thing_lists_bundle(self, screen, qb, False)

# =========================================================

class test_item_assignment(AuthTest):
  "Direct test of kit things and kit item assignment."
  fixtures = [ 'room', 'items', 'kit' ]

  def test_satisfaction_methods(self):
    # Create some kit requests for different numbers of projectors
    disco = self.get_disco()
    krproj2 = KitRequest(kind=self.get_proj(), count=2, setupAssistance=False, notes='')
    krproj2.save()
    krproj4 = KitRequest(kind=self.get_proj(), count=4, setupAssistance=False, notes='')
    krproj4.save()
    # Assign the requests to an item
    disco.kitRequests.add(krproj2)
    disco.kitRequests.add(krproj4)
  
    # Create kit things for projectors with the same counts.
    ktproj2 = KitThing(name='Proj2', kind=self.get_proj(), count=2, coordinator='Bob')
    ktproj2.save()
    ktproj4 = KitThing(name='Proj4', kind=self.get_proj(), count=4, coordinator='Bob')
    ktproj4.save()
  
    # Make sure that kit assignments with the same count or greater will
    # satisfy a request, but not one with fewer.

    # Assign the smaller request to an item.
    kiaproj2 = KitItemAssignment(item=disco, thing=ktproj2)
    kiaproj2.save()
    self.assertTrue(disco.has_unsatisfied_kit_requests())
    self.assertFalse(disco.satisfies_kit_requests())

    # Assign the larger request to an item as well. Should now be enough.
    kiaproj4 = KitItemAssignment(item=disco, thing=ktproj4)
    kiaproj4.save()
    self.assertFalse(disco.has_unsatisfied_kit_requests())
    self.assertTrue(disco.satisfies_kit_requests())
  
    # Alter the kit requests, so that the same overall amount is
    # required, but a different split.
    krproj2.count = 1
    krproj2.save()
    krproj1 = krproj2
    krproj4.count = 5
    krproj4.save()
    krproj5 = krproj4

    # Things should still be satisfied.
    self.assertFalse(disco.has_unsatisfied_kit_requests())
    self.assertTrue(disco.satisfies_kit_requests())

# =========================================================

class test_room_assignment(AuthTest):
  "Direct test of kit things and kit room assignment."
  fixtures = [ 'room', 'items', 'kit' ]

  def test_satisfaction_methods(self):
    # Create some kit requests for different numbers of projectors
    disco = self.get_disco()
    krproj2 = KitRequest(kind=self.get_proj(), count=2, setupAssistance=False, notes='')
    krproj2.save()
    krproj4 = KitRequest(kind=self.get_proj(), count=4, setupAssistance=False, notes='')
    krproj4.save()
  
    # Assign the requests to an item.
    disco.kitRequests.add(krproj2)
    disco.kitRequests.add(krproj4)

    # Create kit things for projectors with the same counts.
    ktproj2 = KitThing(name='Proj2', kind=self.get_proj(), count=2, coordinator='Bob')
    ktproj2.save()
    ktproj4 = KitThing(name='Proj4', kind=self.get_proj(), count=4, coordinator='Bob')
    ktproj4.save()
  
    # Assign the smaller kit things to the item's room, for the same period.
    kraproj2 = KitRoomAssignment(room=disco.room, thing=ktproj2,
                                 fromSlot=disco.start, toSlot=disco.start, toLength=disco.length)
    kraproj2.save()

  
    # Basic checks of the comparison logic.
    # Starts-before also includes "at the same time"
    self.assertTrue(kraproj2.starts_before_slot(slot=disco.start, mins=0))
    # Same for finishes-after
    self.assertTrue(kraproj2.finishes_after_slot(slot=disco.start, mins=disco.length.length))

    # This is therefore true for the item comparisons
    self.assertTrue(kraproj2.starts_before(item=disco))
    self.assertTrue(kraproj2.finishes_after(item=disco))

    # And that means we should be covering the item.
    self.assertTrue(kraproj2.covers(disco))

    # We must certainly overlap the item's period, since we've copied it.
    self.assertTrue(kraproj2.overlaps(disco))

    # This smaller count should not satisfy the item.
    self.assertFalse(disco.satisfies_kit_requests())
    self.assertTrue(disco.has_unsatisfied_kit_requests())

    # Now add the larger assignment, too.
    kraproj4 = KitRoomAssignment(room=disco.room, thing=ktproj4,
                                 fromSlot=disco.start, toSlot=disco.start, toLength=disco.length)
    kraproj4.save()

    # Basic checks of the comparison logic.
    # Starts-before also includes "at the same time"
    self.assertTrue(kraproj4.starts_before_slot(slot=disco.start, mins=0))
    # Same for finishes-after
    self.assertTrue(kraproj4.finishes_after_slot(slot=disco.start, mins=disco.length.length))

    # This is therefore true for the item comparisons
    self.assertTrue(kraproj4.starts_before(item=disco))
    self.assertTrue(kraproj4.finishes_after(item=disco))

    # And that means we should be covering the item.
    self.assertTrue(kraproj4.covers(disco))

    # We must certainly overlap the item's period, since we've copied it.
    self.assertTrue(kraproj4.overlaps(disco))

    # And the two room assignments overlap each other.
    self.assertTrue(kraproj2.overlaps_room_assignment(kraproj4))
    self.assertTrue(kraproj2.overlaps_room_assignment(kraproj2))
    self.assertTrue(kraproj4.overlaps_room_assignment(kraproj4))
    self.assertTrue(kraproj4.overlaps_room_assignment(kraproj2))

    # We now expect to satisfy the item's requests.
    self.assertTrue(disco.satisfies_kit_requests())
    self.assertFalse(disco.has_unsatisfied_kit_requests())

# =========================================================

class test_satisfaction(AuthTest):
  "Satisfying Kit Requests."
  fixtures = [ 'room', 'items', 'tags', 'kit' ]

  ItemsWithUnsatisfiedKitReqs = "Items with unsatisfied kit requests"
  KitClashes = "Kit clashes"

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def req_proj(self, count=1):
    return default_kitrequest({ "count": count, "kind": self.get_proj().id })
  def req_screen(self, count=1):
    return default_kitrequest({ "count": count, "kind": self.get_screen().id })
  def proj_thing(self, count=1):
    return default_kitthing({ "count": count, "kind": self.get_proj().id })
  def screen_thing(self, count=1):
    return default_kitthing({ "count": count, "kind": self.get_screen().id })

  def add_req_to_item(self, req, item):
    nreqs = item.kitRequests.count()
    addurl = reverse('add_kitrequest_to_item', args=[ item.id ])

    # Add the kit req.
    self.response = self.client.post(addurl, req, follow=True)
    self.status_okay()
    self.assertEqual(nreqs+1, item.kitRequests.count())

  def test_item_not_satisfied(self):
    "Check that reqs on items are correctly not satisfied, when not fulfilled."

    disco = self.get_disco()
    req = self.req_proj()
    self.assertEqual(disco.kitRequests.count(), 0)
    self.assertEqual(disco.kit.count(), 0)
    self.add_req_to_item(req, disco)
    self.assertEqual(disco.kitRequests.count(), 1)
    # convert our dict back into the proper request
    req = disco.kitRequests.all()[0]

    # There's no KitThing on this item that satisfies the request.
    # Nor is there a KitThing on the room that satisfies it.

    # Check directly
    self.assertFalse(disco.satisfies_kit_requests())
    self.assertTrue(disco.has_unsatisfied_kit_requests())

    # Check indirectly
    check_lists_item(self, self.ItemsWithUnsatisfiedKitReqs, disco, True)

    # Change the req to have a larger count.

    req.count = 8
    req.save()

    # Add a Kit Thing of the correct type, but insufficient count.
    projname = 'huckleberry'
    self.response = self.client.post(reverse('new_kitthing'), default_kitthing({
      "name": projname,
      "kind": self.get_proj().id,
      "count": 4
    }), follow=True)
    self.status_okay()
    self.form_okay()

    # Fetch that new item
    ktproj = KitThing.objects.get(name=projname)

    # Add a Kit Thing of the correct count, but wrong type.
    scrname = 'snagglepuss'
    self.response = self.client.post(reverse('new_kitthing'), default_kitthing({
      "name": scrname,
      "kind": self.get_screen().id,
      "count": 8
    }), follow=True)
    self.status_okay()
    self.form_okay()

    # Fetch that new item
    ktscr = KitThing.objects.get(name=scrname)

    # Add the things to the item.

    item_lists_thing(self, disco, ktproj, False)
    item_lists_thing(self, disco, ktscr, False)
    self.response = self.client.post(reverse('add_kitthing_to_item'), {
      "thing": ktproj.id,
      "item": disco.id
    }, follow=True)
    self.status_okay()
    self.form_okay()
    self.response = self.client.post(reverse('add_kitthing_to_item'), {
      "thing": ktscr.id,
      "item": disco.id
    }, follow=True)
    self.status_okay()
    self.form_okay()

    # There's still no KitThing on this item that satisfies the request.
    # Nor is there a KitThing on the room that satisfies it.

    # Check directly
    self.assertFalse(disco.satisfies_kit_requests())
    self.assertTrue(disco.has_unsatisfied_kit_requests())

    # Check indirectly
    check_lists_item(self, self.ItemsWithUnsatisfiedKitReqs, disco, True)

    # Remove the KitThings from the item
    KitItemAssignment.objects.get(thing=ktproj, item=disco).delete()
    KitItemAssignment.objects.get(thing=ktscr, item=disco).delete()

    # Attach the things to a room
    morning = self.get_morning()
    evening = self.get_evening()
    hour = self.get_hour()

    self.response = self.client.post(reverse('add_kitthing_to_room'), {
      "thing": ktproj.id,
      "room": disco.room.id,
      "fromSlot": morning.id,
      "toSlot": evening.id,
      "toLength": hour.id
    }, follow=True)
    self.status_okay()
    self.form_okay()

    self.response = self.client.post(reverse('add_kitthing_to_room'), {
      "thing": ktscr.id,
      "room": disco.room.id,
      "fromSlot": morning.id,
      "toSlot": evening.id,
      "toLength": hour.id
    }, follow=True)
    self.status_okay()
    self.form_okay()

    # And neither of those should satisfy the item's request.

    # Check directly
    self.assertFalse(disco.satisfies_kit_requests())
    self.assertTrue(disco.has_unsatisfied_kit_requests())

    # Check indirectly
    check_lists_item(self, self.ItemsWithUnsatisfiedKitReqs, disco, True)

    # Clean up again
    KitRoomAssignment.objects.get(thing=ktproj, room=disco.room).delete()
    KitRoomAssignment.objects.get(thing=ktscr, room=disco.room).delete()

    # Change both the KitThings to have the correct type/count
    ktproj.count = req.count
    ktproj.kind = req.kind
    ktscr.count = req.count
    ktscr.kind = req.kind
    ktproj.save()
    ktscr.save()

    # Tweak the room assignments to miss the item.
    # Make sure we exclude undefined slots, though.
    slots_before = Slot.objects.filter(start__lt=disco.start.start, day=disco.start.day, isUndefined=False).reverse()
    slot_before = slots_before[0]
    slots_after = Slot.objects.filter(start__gt=disco.start.start, day=disco.start.day, isUndefined=False)
    slot_after = slots_after[0]


    self.response = self.client.post(reverse('add_kitthing_to_room'), {
      "thing": ktproj.id,
      "room": disco.room.id,
      "fromSlot": morning.id,
      "toSlot": slot_before.id,
      "toLength": hour.id
    }, follow=True)
    self.status_okay()
    self.form_okay()

    self.response = self.client.post(reverse('add_kitthing_to_room'), {
      "thing": ktscr.id,
      "room": disco.room.id,
      "fromSlot": slot_after.id,
      "toSlot": evening.id,
      "toLength": hour.id
    }, follow=True)
    self.status_okay()
    self.form_okay()

    # Should still not be satisfying req

    # Check directly
    self.assertFalse(disco.satisfies_kit_requests())
    self.assertTrue(disco.has_unsatisfied_kit_requests())

    # Check indirectly
    check_lists_item(self, self.ItemsWithUnsatisfiedKitReqs, disco, True)

    # Change one of the room assignments so that it covers the item's slot.
    kra = KitRoomAssignment.objects.get(room=disco.room, thing=ktproj)
    kra.toSlot = disco.start
    kra.toLength = disco.length
    kra.save()

    # At this point, the assignment SHOULD satisfy the req.
    self.assertFalse(disco.has_unsatisfied_kit_requests())

    # create ANOTHER request that is satisfied by assignments.
    req2 = self.req_proj()
    req2['count'] = ktproj.count
    self.add_req_to_item(req2, disco)
    req2 = disco.kitRequests.all()[0]

    # So now we have two reqs on the item, and the assignments to room
    # can satisfy one, but not both.

    # Check directly
    self.assertFalse(disco.satisfies_kit_requests())
    self.assertTrue(disco.has_unsatisfied_kit_requests())

    # Check indirectly
    check_lists_item(self, self.ItemsWithUnsatisfiedKitReqs, disco, True)
# =========================================================

class test_room_availability(AuthTest):
  "Direct test of room availability."
  fixtures = [ 'room', 'items' ]

  def test_never_and_always(self):

    # Get some rooms to play with
    ops = self.get_ops()
    video = self.get_video()

    # Neither should have any availability yet
    self.assertEqual(ops.availability.count(), 0)
    self.assertEqual(video.availability.count(), 0)
    self.assertTrue(ConInfoBool.objects.no_avail_means_always_avail())

    # So we should consider them always available.
    self.assertTrue(ops.always_available())
    self.assertTrue(video.always_available())
    self.assertFalse(ops.never_available())
    self.assertFalse(video.never_available())

    # Let's add a slot to each.
    ops.availability.add(self.get_morning())
    ops.save()
    video.availability.add(self.get_evening())
    video.save()

    # So should no longer be always available, or never available.
    self.assertFalse(ops.always_available())
    self.assertFalse(video.always_available())
    self.assertFalse(ops.never_available())
    self.assertFalse(video.never_available())

    # Change the setting for the con default.
    no_avail = ConInfoBool.objects.get(var='no_avail_means_always_avail')
    no_avail.val = False
    no_avail.save()
    self.assertFalse(ConInfoBool.objects.no_avail_means_always_avail())

    # Shouldn't have affected the rooms' status, though.
    self.assertFalse(ops.always_available())
    self.assertFalse(video.always_available())
    self.assertFalse(ops.never_available())
    self.assertFalse(video.never_available())

    # Until we remove their availability again
    ops.availability.remove(self.get_morning())
    ops.save()
    video.availability.remove(self.get_evening())
    ops.save()
    self.assertEqual(ops.availability.count(), 0)
    self.assertEqual(video.availability.count(), 0)

    # And now we should treat that as never available.
    self.assertFalse(ops.always_available())
    self.assertFalse(video.always_available())
    self.assertTrue(ops.never_available())
    self.assertTrue(video.never_available())

  def test_available_for_item(self):

    # Get a room with an item
    disco = self.get_disco()
    room = disco.room

    # No avail yet
    self.assertEqual(room.availability.count(), 0)

    # But is always available, so should be available for the item
    self.assertTrue(room.always_available())
    self.assertTrue(room.available_for(disco))

    # Add a slot that doesn't cover the disco - that should stop the
    # always-available, and will mean the room is no longer available
    # for the disco.
    room.availability.add(self.get_morning())
    self.assertFalse(room.always_available())
    self.assertFalse(room.available_for(disco))

    # Get the slots that cover the disco
    slots = disco.slots()
    self.assertTrue(len(slots) == 2)

    # Add the first. Should not be enough.
    room.availability.add(slots[0])
    self.assertFalse(room.available_for(disco))

    # Remove that, and add the last. Should not be enough.
    room.availability.remove(slots[0])
    room.availability.add(slots[1])
    self.assertFalse(room.available_for(disco))

    # Add all. Should now be available.
    room.availability.add(slots[0])
    self.assertTrue(room.available_for(disco))

    # Remove them both, again.
    
    room.availability.remove(slots[0])
    room.availability.remove(slots[1])

    # Add all slots on the same day. Will be available.
    for s in Slot.objects.filter(day=slots[0].day):
      room.availability.add(s)
    self.assertTrue(room.available_for(disco))

    # remove one of the item's slots. No longer available.
    room.availability.remove(slots[0])
    self.assertFalse(room.available_for(disco))

    # Get a different day, and make the room available for
    # all of that day.
    sunday = self.get_sunday()
    self.assertNotEqual(sunday, disco.start.day)
    for s in Slot.objects.filter(day=sunday):
      room.availability.add(s)
    self.assertFalse(room.available_for(disco))

# =========================================================

class test_person_availability(AuthTest):
  "Direct test of person availability."
  fixtures = [ 'room', 'person', 'items' ]

  def test_never_and_always(self):

    # Get some people to play with
    buffy = self.get_buffy()
    giles = self.get_giles()

    # Neither should have any availability yet
    self.assertEqual(buffy.availability.count(), 0)
    self.assertEqual(giles.availability.count(), 0)
    self.assertTrue(ConInfoBool.objects.no_avail_means_always_avail())

    # So we should consider them always available.
    self.assertTrue(buffy.always_available())
    self.assertTrue(giles.always_available())
    self.assertFalse(buffy.never_available())
    self.assertFalse(giles.never_available())

    # Let's add a slot to each.
    buffy.availability.add(self.get_morning())
    buffy.save()
    giles.availability.add(self.get_evening())
    giles.save()

    # So should no longer be always available, or never available.
    self.assertFalse(buffy.always_available())
    self.assertFalse(giles.always_available())
    self.assertFalse(buffy.never_available())
    self.assertFalse(giles.never_available())

    # Change the setting for the con default.
    no_avail = ConInfoBool.objects.get(var='no_avail_means_always_avail')
    no_avail.val = False
    no_avail.save()
    self.assertFalse(ConInfoBool.objects.no_avail_means_always_avail())

    # Shouldn't have affected the people's status, though.
    self.assertFalse(buffy.always_available())
    self.assertFalse(giles.always_available())
    self.assertFalse(buffy.never_available())
    self.assertFalse(giles.never_available())

    # Until we remove their availability again
    buffy.availability.remove(self.get_morning())
    buffy.save()
    giles.availability.remove(self.get_evening())
    buffy.save()
    self.assertEqual(buffy.availability.count(), 0)
    self.assertEqual(giles.availability.count(), 0)

    # And now we should treat that as never available.
    self.assertFalse(buffy.always_available())
    self.assertFalse(giles.always_available())
    self.assertTrue(buffy.never_available())
    self.assertTrue(giles.never_available())

  def test_available_for_item(self):

    # Get a person and an item
    disco = self.get_disco()
    buffy = self.get_buffy()

    # No avail yet
    self.assertEqual(buffy.availability.count(), 0)

    # But is always available, so should be available for the item
    self.assertTrue(buffy.always_available())
    self.assertTrue(buffy.available_for(disco))

    # Add a slot that doesn't cover the disco - that should stop the
    # always-available, and will mean the buffy is no longer available
    # for the disco.
    buffy.availability.add(self.get_morning())
    self.assertFalse(buffy.always_available())
    self.assertFalse(buffy.available_for(disco))

    # Get the slots that cover the disco
    slots = disco.slots()
    self.assertTrue(len(slots) == 2)

    # Add the first. Should not be enough.
    buffy.availability.add(slots[0])
    self.assertFalse(buffy.available_for(disco))

    # Remove that, and add the last. Should not be enough.
    buffy.availability.remove(slots[0])
    buffy.availability.add(slots[1])
    self.assertFalse(buffy.available_for(disco))

    # Add all. Should now be available.
    buffy.availability.add(slots[0])
    self.assertTrue(buffy.available_for(disco))

    # Remove them both, again.
    
    buffy.availability.remove(slots[0])
    buffy.availability.remove(slots[1])

    # Add all slots on the same day. Will be available.
    for s in Slot.objects.filter(day=slots[0].day):
      buffy.availability.add(s)
    self.assertTrue(buffy.available_for(disco))

    # remove one of the item's slots. No longer available.
    buffy.availability.remove(slots[0])
    self.assertFalse(buffy.available_for(disco))

    # Get a different day, and make the buffy available for
    # all of that day.
    sunday = self.get_sunday()
    self.assertNotEqual(sunday, disco.start.day)
    for s in Slot.objects.filter(day=sunday):
      buffy.availability.add(s)
    self.assertFalse(buffy.available_for(disco))

# =========================================================

class test_kit_availability(AuthTest):
  "Direct test of kit availability."
  fixtures = [ 'room', 'items', 'kit' ]

  def test_never_and_always(self):

    # Get some stuff to play with
    proj = self.get_greenroomproj()
    screen = self.get_greenroomscr()

    # Neither should have any availability yet
    self.assertEqual(proj.availability.count(), 0)
    self.assertEqual(screen.availability.count(), 0)
    self.assertTrue(ConInfoBool.objects.no_avail_means_always_avail())

    # So we should consider them always available.
    self.assertTrue(proj.always_available())
    self.assertTrue(screen.always_available())
    self.assertFalse(proj.never_available())
    self.assertFalse(screen.never_available())

    # Let's add a slot to each.
    proj.availability.add(self.get_morning())
    proj.save()
    screen.availability.add(self.get_evening())
    screen.save()

    # So should no longer be always available, or never available.
    self.assertFalse(proj.always_available())
    self.assertFalse(screen.always_available())
    self.assertFalse(proj.never_available())
    self.assertFalse(screen.never_available())

    # Change the setting for the con default.
    no_avail = ConInfoBool.objects.get(var='no_avail_means_always_avail')
    no_avail.val = False
    no_avail.save()
    self.assertFalse(ConInfoBool.objects.no_avail_means_always_avail())

    # Shouldn't have affected the things' status, though.
    self.assertFalse(proj.always_available())
    self.assertFalse(screen.always_available())
    self.assertFalse(proj.never_available())
    self.assertFalse(screen.never_available())

    # Until we remove their availability again
    proj.availability.remove(self.get_morning())
    proj.save()
    screen.availability.remove(self.get_evening())
    proj.save()
    self.assertEqual(proj.availability.count(), 0)
    self.assertEqual(screen.availability.count(), 0)

    # And now we should treat that as never available.
    self.assertFalse(proj.always_available())
    self.assertFalse(screen.always_available())
    self.assertTrue(proj.never_available())
    self.assertTrue(screen.never_available())

  def test_available_for_item(self):

    # Get a thing and an item
    disco = self.get_disco()
    proj = self.get_greenroomproj()

    # No avail yet
    self.assertEqual(proj.availability.count(), 0)

    # But is always available, so should be available for the item
    self.assertTrue(proj.always_available())
    self.assertTrue(proj.available_for(disco))

    # Add a slot that doesn't cover the disco - that should stop the
    # always-available, and will mean the proj is no longer available
    # for the disco.
    proj.availability.add(self.get_morning())
    self.assertFalse(proj.always_available())
    self.assertFalse(proj.available_for(disco))

    # Get the slots that cover the disco
    slots = disco.slots()
    self.assertTrue(len(slots) == 2)

    # Add the first. Should not be enough.
    proj.availability.add(slots[0])
    self.assertFalse(proj.available_for(disco))

    # Remove that, and add the last. Should not be enough.
    proj.availability.remove(slots[0])
    proj.availability.add(slots[1])
    self.assertFalse(proj.available_for(disco))

    # Add all. Should now be available.
    proj.availability.add(slots[0])
    self.assertTrue(proj.available_for(disco))

    # Remove them both, again.
    
    proj.availability.remove(slots[0])
    proj.availability.remove(slots[1])

    # Add all slots on the same day. Will be available.
    for s in Slot.objects.filter(day=slots[0].day):
      proj.availability.add(s)
    self.assertTrue(proj.available_for(disco))

    # remove one of the item's slots. No longer available.
    proj.availability.remove(slots[0])
    self.assertFalse(proj.available_for(disco))

    # Get a different day, and make the proj available for
    # all of that day.
    sunday = self.get_sunday()
    self.assertNotEqual(sunday, disco.start.day)
    for s in Slot.objects.filter(day=sunday):
      proj.availability.add(s)
    self.assertFalse(proj.available_for(disco))

  def test_kit_avail_for_room(self):

    # Get a room, a thing and some slots.
    disco = self.get_disco()
    ops = self.get_ops()
    proj = self.get_greenroomproj()

    self.assertEqual(ops.availability.count(), 0)
    self.assertEqual(proj.availability.count(), 0)

    # Give each of them a slot, so that they're not always available
    ops.availability.add(self.get_morning())
    proj.availability.add(self.get_morning())
    self.assertFalse(ops.always_available())
    self.assertFalse(proj.always_available())

    # Assign the thing to the room for some slots
    kra = KitRoomAssignment(room=ops, thing=proj, fromSlot=disco.start, toSlot=disco.start, toLength=disco.length)
    kra.save()

    # Neither the room nor the thing should be available
    self.assertFalse(ops.available_for(kra))
    self.assertFalse(proj.available_for(kra))

    # Add all the slots for the days of the item.
    for s in Slot.objects.filter(day=disco.start.day):
      ops.availability.add(s)
    self.assertTrue(ops.available_for(kra))
    self.assertFalse(proj.available_for(kra))
    for s in Slot.objects.filter(day=disco.start.day):
      proj.availability.add(s)
    self.assertTrue(ops.available_for(kra))
    self.assertTrue(proj.available_for(kra))

    # Zap the relevant slot from their availability
    ops.availability.remove(disco.start)
    self.assertFalse(ops.available_for(kra))
    self.assertTrue(proj.available_for(kra))
    proj.availability.remove(disco.start)
    self.assertFalse(ops.available_for(kra))
    self.assertFalse(proj.available_for(kra))

# =========================================================

class test_slot_items(AuthTest):
  "Test what appears in slot item methods."
  fixtures = [ 'room', 'items', 'person' ]

  def test_starting_direct(self):
    """
    Check that a slot knowns the difference between 'item occupies slot'
    and 'item starts in slot'.
    """
    # Snarf the usual items
    disco = self.get_disco()
    cabaret = self.get_cabaret()
    ceilidh = self.get_ceilidh()

    friday09 = Slot.objects.get(startText='9pm', day__name='Friday')
    friday10 = Slot.objects.get(startText='10pm', day__name='Friday')

    self.assertEqual(friday09, cabaret.start)
    self.assertEqual(friday10, disco.start)
    self.assertEqual(friday10, ceilidh.start)

    for i in [ disco, cabaret, ceilidh ]:
      self.assertTrue(i in friday10.items())
    for i in [ ceilidh, disco ]:
      self.assertTrue(i in friday10.items_starting())
      self.assertFalse(i in friday09.items_starting())
      self.assertFalse(i in friday09.items())

  def test_starting_indirect(self):
    """
    Look at the views for given slots, and check which items they display.
    """
    # Grab a room
    ops = self.get_ops()

    # Snarf the usual items
    disco = self.get_disco()
    cabaret = self.get_cabaret()
    ceilidh = self.get_ceilidh()

    # Move one of them to a different room.
    self.assertEqual(disco.room, cabaret.room)
    self.assertEqual(ceilidh.room, cabaret.room)
    self.assertNotEqual(disco.room, ops)
    disco.room = ops
    disco.save()

    friday09 = Slot.objects.get(startText='9pm', day__name='Friday')
    friday10 = Slot.objects.get(startText='10pm', day__name='Friday')

    self.assertEqual(friday09, cabaret.start)
    self.assertEqual(friday10, disco.start)
    self.assertEqual(friday10, ceilidh.start)

    # Check what appears in the items and items_starting lists for each slot.
    # No room specified yet.
    # We expect:
    # 9pm: items: cabaret
    # 9pm starting: cabaret
    # 10pm: items: disco, cabaret, ceilidh
    # 10pm: starting: disco, ceilidh

    self.response = self.client.get(reverse('show_slot_detail', args=[friday09.id]))
    self.status_okay()
    self.has_row('itable', { "title": cabaret.title })
    self.has_row('itable_starting', { "title": cabaret.title })
    self.no_row('itable', { "title": disco.title })
    self.no_row('itable_starting', { "title": disco.title })
    self.no_row('itable', { "title": ceilidh.title })
    self.no_row('itable_starting', { "title": ceilidh.title })

    self.response = self.client.get(reverse('show_slot_detail', args=[friday10.id]))
    self.status_okay()
    self.has_row('itable', { "title": cabaret.title })
    self.no_row('itable_starting', { "title": cabaret.title })
    self.has_row('itable', { "title": disco.title })
    self.has_row('itable_starting', { "title": disco.title })
    self.has_row('itable', { "title": ceilidh.title })
    self.has_row('itable_starting', { "title": ceilidh.title })

    # Now be specific about the room, and check that we only see items that
    # occur in that room. We don't have a page that shows this, so we have
    # to check directly.

    for i in [ disco, cabaret, ceilidh ]:
      self.assertTrue(i in friday10.items())
    for i in [ disco, ceilidh ]:
      self.assertTrue(i in friday10.items_starting())
      self.assertFalse(i in friday09.items_starting())
      self.assertFalse(i in friday09.items())
    self.assertTrue(cabaret in friday09.items())
    self.assertTrue(cabaret in friday09.items_starting())

    # We expect:
    # 9pm main hall: items: cabaret
    # 9pm main hall starting: cabaret
    # 10pm main hall: items: cabaret, ceilidh
    # 10pm main hall: starting: ceilidh

    rm = cabaret.room
    self.assertTrue(cabaret in friday09.items(rm))
    self.assertTrue(cabaret in friday09.items_starting(rm))
    for i in [ disco, ceilidh ]:
      self.assertFalse(i in friday09.items_starting(rm))
      self.assertFalse(i in friday09.items(rm))
    for i in [ cabaret, ceilidh ]:
      self.assertTrue(i in friday10.items(rm))
    self.assertTrue(ceilidh in friday10.items_starting(rm))
    self.assertFalse(cabaret in friday10.items_starting(rm))
    self.assertFalse(disco in friday10.items_starting(rm))
    self.assertFalse(disco in friday10.items(rm))

    # We expect:
    # 9pm ops: items: nothing
    # 9pm ops starting: nothing
    # 10pm ops: items: disco
    # 10pm ops: starting: disco

    for i in [ disco, cabaret, ceilidh ]:
      self.assertFalse(i in friday09.items(ops))
      self.assertFalse(i in friday09.items_starting(ops))
    for i in [ cabaret, ceilidh ]:
      self.assertFalse(i in friday10.items(ops))
      self.assertFalse(i in friday10.items_starting(ops))
    self.assertTrue(disco in friday10.items(ops))
    self.assertTrue(disco in friday10.items_starting(ops))

class test_grids(AuthTest):
  "Direct test of what appears in grid cells."
  fixtures = [ 'room', 'items', 'person' ]

  def test_list_grids(self):
    self.response = self.client.get(reverse('list_grids'))
    self.status_okay()
    self.assertNotEqual(Grid.objects.count(), 0)
    for g in Grid.objects.all():
      self.has_row('gtable', { 'name': g.name })
      self.has_link_to('show_grid', args=[int(g.id)])

  def test_items_in_cells(self):
    "Check the items() methods on slots and rooms."
    # Get some items
    disco = self.get_disco()
    cabaret = self.get_cabaret()
    bidsession = self.get_bidsession()

    cabaret.visible = False
    cabaret.save()

    self.assertTrue(disco.visible)
    self.assertTrue(bidsession.visible)
    self.assertFalse(cabaret.visible)

    self.assertEqual(len(disco.slots()), 2)
    self.assertEqual(len(cabaret.slots()), 2)
    self.assertEqual(len(bidsession.slots()), 1)

    # Verify that for each of these items, the Slots and Rooms also think
    # that the item is scheduled there.

    for i in [ disco, cabaret, bidsession ]:
      self.assertTrue(i in i.room.items())
      for s in i.slots():
        self.assertTrue(i in i.room.items(s))
        self.assertTrue(i in s.items())
        self.assertTrue(i in s.items(i.room))

    # Verify that the visible items appear in items_public(), but the
    # non-visible item does not.

    for i in [ disco, bidsession ]:
      self.assertTrue(i in i.room.items_public())
      for s in i.slots():
        self.assertTrue(i in i.room.items_public(s))
        self.assertTrue(i in s.items_public())
        self.assertTrue(i in s.items_public(i.room))

    for i in [ cabaret ]:
      self.assertFalse(i in i.room.items_public())
      for s in i.slots():
        self.assertFalse(i in i.room.items_public(s))
        self.assertFalse(i in s.items_public())
        self.assertFalse(i in s.items_public(i.room))

    # Verify that the items don't appear in other rooms or other slots.

    for i in [ disco, cabaret, bidsession ]:
      for r in Room.objects.exclude(id=i.room.id):
        self.assertFalse(i in r.items())
        for s in Slot.objects.all():
          self.assertFalse(i in r.items(s))
          self.assertFalse(i in s.items(r))
      for s in Slot.objects.exclude(id__in=[ s.id for s in i.slots() ]):
        self.assertFalse(i in s.items())
        for r in Room.objects.all():
          self.assertFalse(i in s.items(r))

  def test_people_on_items_in_cells(self):
    "Check that people are visible on items in cells (or not)."

    disco = self.get_disco()
    cabaret = self.get_cabaret()
    bidsession = self.get_bidsession()

    buffy = self.get_buffy()
    giles = self.get_giles()
    dawn = self.get_dawn()

    # XXX There's a question of a bug here. If we make an item non-visible,
    # should that make us treat all the people as non-visible too, regardless
    # of how they've been added? Should we just make that a Check?
    bidsession.visible = False
    bidsession.save()

    self.assertTrue(disco.visible)
    self.assertTrue(cabaret.visible)
    self.assertFalse(bidsession.visible)

    # Add each of the people to each of the items, but mix-and-match
    # who should be visible on each.

    ip = ItemPerson(item=disco, person=buffy, visible=True)
    ip.save()
    ip = ItemPerson(item=cabaret, person=buffy, visible=True)
    ip.save()
    ip = ItemPerson(item=bidsession, person=buffy, visible=True)
    ip.save()
    ip = ItemPerson(item=disco, person=giles, visible=False)
    ip.save()
    ip = ItemPerson(item=cabaret, person=giles, visible=False)
    ip.save()
    ip = ItemPerson(item=bidsession, person=giles, visible=False)
    ip.save()
    ip = ItemPerson(item=disco, person=dawn, visible=True)
    ip.save()
    ip = ItemPerson(item=cabaret, person=dawn, visible=True)
    ip.save()
    ip = ItemPerson(item=bidsession, person=dawn, visible=False)
    ip.save()

    # Everyone should all be returned by the people lists, because they don't filter.

    for p in [ buffy, giles, dawn ]:
      for i in [ disco, cabaret, bidsession ]:
        self.assertTrue(p in i.people.all())

    # Buffy should also be in the public list for each item, but Giles should not be.

    for i in [ disco, cabaret, bidsession ]:
      self.assertTrue(buffy in i.people_public())
      self.assertFalse(giles in i.people_public())

    # Dawn should be in the public list for disco and cabaret, but not the big session.
    self.assertTrue(dawn in disco.people_public())
    self.assertTrue(dawn in cabaret.people_public())
    self.assertFalse(dawn in bidsession.people_public())

class test_grids_public(NonauthTest):
  "Test what the templates retrieve, for grids."
  fixtures = [ 'room', 'items', 'person' ]

  def test_people_on_items_in_cells(self):
    "Check that people are visible on items in cells (or not)."

    disco = self.get_disco()
    cabaret = self.get_cabaret()
    bidsession = self.get_bidsession()

    buffy = self.get_buffy()
    giles = self.get_giles()
    dawn = self.get_dawn()

    bidsession.visible = False
    bidsession.save()

    self.assertTrue(disco.visible)
    self.assertTrue(cabaret.visible)
    self.assertFalse(bidsession.visible)

    # Move each of these items to 10pm, on consecutive days

    disco.start = Slot.objects.get(startText='10pm', day__name='Friday')
    disco.save()
    cabaret.start = Slot.objects.get(startText='10pm', day__name='Saturday')
    cabaret.save()
    bidsession.start = Slot.objects.get(startText='10pm', day__name='Sunday')
    bidsession.save()

    # Add each of the people to each of the items, but mix-and-match
    # who should be visible on each.

    ip = ItemPerson(item=disco, person=buffy, visible=True)
    ip.save()
    ip = ItemPerson(item=cabaret, person=buffy, visible=True)
    ip.save()
    ip = ItemPerson(item=bidsession, person=buffy, visible=True)
    ip.save()
    ip = ItemPerson(item=disco, person=giles, visible=False)
    ip.save()
    ip = ItemPerson(item=cabaret, person=giles, visible=False)
    ip.save()
    ip = ItemPerson(item=bidsession, person=giles, visible=False)
    ip.save()
    ip = ItemPerson(item=disco, person=dawn, visible=True)
    ip.save()
    ip = ItemPerson(item=cabaret, person=dawn, visible=True)
    ip.save()
    ip = ItemPerson(item=bidsession, person=dawn, visible=False)
    ip.save()

    # Everyone but Giles should be visible, for the disco

    grid = Grid.objects.get(name='Friday 10pm-2am')
    self.assertTrue(disco.start in grid.slots.all())
    self.response = self.client.get(reverse('show_grid', kwargs={ "gr": grid.id }))
    self.status_okay()
    self.has_link_to('show_item_detail', args=[int(disco.id)])
    self.has_link_to('show_person_detail', args=[int(buffy.id)])
    self.has_link_to('show_person_detail', args=[int(dawn.id)])
    self.no_link_to('show_person_detail', args=[int(giles.id)])

    # Buffy and Dawn are visible on the cabaret, but Giles is not.

    grid = Grid.objects.get(name='Saturday 10pm-2am')
    self.assertTrue(cabaret.start in grid.slots.all())
    self.response = self.client.get(reverse('show_grid', kwargs={ "gr": grid.id }))
    self.status_okay()
    self.has_link_to('show_item_detail', args=[int(cabaret.id)])
    self.has_link_to('show_person_detail', args=[int(buffy.id)])
    self.has_link_to('show_person_detail', args=[int(dawn.id)])
    self.no_link_to('show_person_detail', args=[int(giles.id)])

    # The bid session isn't visible, so we shouldn't see it, or anyone on it.

    grid = Grid.objects.get(name='Sunday 10pm-2am')
    self.assertTrue(bidsession.start in grid.slots.all())
    self.response = self.client.get(reverse('show_grid', kwargs={ "gr": grid.id }))
    self.status_okay()
    self.no_link_to('show_item_detail', args=[int(bidsession.id)])
    self.no_link_to('show_person_detail', args=[int(buffy.id)])
    self.no_link_to('show_person_detail', args=[int(dawn.id)])
    self.no_link_to('show_person_detail', args=[int(giles.id)])

class test_coninfo(NonauthTest):
  "Check the values for ConInfo"

  def test_coninfobool(self):
    "Check boolean-valued con settings"
    self.assertTrue(ConInfoBool.objects.show_shortname())
    self.assertFalse(ConInfoBool.objects.rooms_across_top())
    self.assertTrue(ConInfoBool.objects.no_avail_means_always_avail())

    show_short = ConInfoBool.objects.get(var='show_shortname')
    self.assertTrue(show_short.val)
    self.assertEqual(str(show_short), u'Show shortnames')

  def test_coninfoint(self):
    "Check integer-valued con settings"
    self.assertEqual(ConInfoInt.objects.max_items_per_day(), 4)
    self.assertEqual(ConInfoInt.objects.max_items_whole_con(), 12)
    self.assertEqual(ConInfoInt.objects.max_consecutive_items(), 2)

    max_day = ConInfoInt.objects.get(var='max_items_per_day')
    self.assertEqual(max_day.val, 4)
    self.assertEqual(str(max_day), u'Max items per day for a person')

  def test_coninfostr(self):
    "Check string-valued con settings"
    self.assertEqual(ConInfoString.objects.con_name(), u'MyCon 2012')
    self.assertEqual(ConInfoString.objects.email_from(), u'steve@whitecrow.demon.co.uk')

    con_name = ConInfoString.objects.get(var='con_name')
    self.assertEqual(con_name.val, u'MyCon 2012')
    self.assertEqual(str(con_name), u'Convention name')

class test_condays(NonauthTest):
  "Check the manager for ConDays."

  def test_when_all_public(self):
    "Check the manager when there are no private days."

    friday = self.get_friday()
    monday = self.get_monday()
    self.assertEqual(friday, ConDay.objects.earliest_day())
    self.assertEqual(friday, ConDay.objects.earliest_public_day())
    self.assertEqual(monday, ConDay.objects.latest_day())
    self.assertEqual(monday, ConDay.objects.latest_public_day())

  def test_when_some_private(self):
    "Check the manager when there are some private days."

    friday = self.get_friday()
    saturday = self.get_saturday()
    sunday = self.get_sunday()
    monday = self.get_monday()

    friday.visible = False
    friday.save()
    monday.visible = False
    monday.save()

    self.assertEqual(friday, ConDay.objects.earliest_day())
    self.assertNotEqual(friday, ConDay.objects.earliest_public_day())
    self.assertEqual(saturday, ConDay.objects.earliest_public_day())
    self.assertEqual(monday, ConDay.objects.latest_day())
    self.assertNotEqual(monday, ConDay.objects.latest_public_day())
    self.assertEqual(sunday, ConDay.objects.latest_public_day())

  def test_when_privacy_reversed(self):
    "Check the manager when there are some private days in the middle."

    friday = self.get_friday()
    saturday = self.get_saturday()
    sunday = self.get_sunday()
    monday = self.get_monday()

    saturday.visible = False
    saturday.save()
    sunday.visible = False
    sunday.save()

    self.assertEqual(friday, ConDay.objects.earliest_day())
    self.assertEqual(friday, ConDay.objects.earliest_public_day())
    self.assertEqual(monday, ConDay.objects.latest_day())
    self.assertEqual(monday, ConDay.objects.latest_public_day())

  def test_TBA(self):
    "Check that the undefined value doesn't turn up for any of the other methods."

    tba = ConDay.objects.find_undefined()
    self.assertNotEqual(tba, ConDay.objects.earliest_day())
    self.assertNotEqual(tba, ConDay.objects.earliest_public_day())
    self.assertNotEqual(tba, ConDay.objects.latest_day())
    self.assertNotEqual(tba, ConDay.objects.latest_public_day())

class test_xml(AuthTest):
  "Pull the XML dump down, and see what's in there."

  fixtures = [ 'room', 'person', 'items', 'tags', 'kit' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_rooms(self):
    "Check all the rooms are listed."

    self.response = self.client.get(reverse('xml_dump'))
    self.status_okay()
    for room in Room.objects.all():
      self.assertTrue(room.name in self.response.content)

  def test_people(self):
    "Check all the people are listed."

    self.response = self.client.get(reverse('xml_dump'))
    self.status_okay()
    for person in Person.objects.all():
      self.assertTrue(person.as_name() in self.response.content)
      self.assertTrue(person.as_badge() in self.response.content)

  def test_items(self):
    "Check all the items are listed."

    self.response = self.client.get(reverse('xml_dump'))
    self.status_okay()
    for item in Item.objects.all():
      self.assertTrue(escape(item.title) in self.response.content)
      self.assertTrue(escape(item.shortname) in self.response.content)

# Tests required
# Items
# 	Satisfaction
# 		included in not-satisfied list
# 		satisfied-by listing is correct
#
# 	Grids
# 		Item appears in slot (room by time)
# 		item appears in slot (time by room)
# 		Long item appears in multiple slots
# 		Long item that starts before grid
# 		long item that ends after grid
# 		Multiple items in same slot
# 		Move item here
# 		Invisible items
# 		Items with noone
# 		Items with visible people
# 			by name
# 			by badge
# 		Items with invisible people
# 		With "fill slot"
# 		Without "fill slot"
# 		Invisible rooms
# 		Unavailable rooms are grey
# 	Checks
# 		No email address
# 		Haven't joined yet
# 		Not complete
# 		people clashes
# 		People not available
# 		items with no people
# 		items with no room
# 		items not scheduled
# 		items with unknown gopher count
# 		items not complete
# 		items with unsatisfied kit requests
# 		kit clashes
# 
# 	Main page
# 		Correct scheduled items
# 		Correct scheduled hours
# 		Correct budget
# 		Correct scheduled panellists
# 		Correct programme participants
# 		Correct item kind distro
# 	XML Dump
# 
# 	Email
# 		For: main person listing, person on item, person with tag
# 			Select all people, when blank
# 			Select all people, when some selected
# 			Deselect all people, when all selected
# 			Deselect all people, when some selected
# 			Save as list, with default name
# 			Save as list, with new name.
# 			Save as list, edited.
# 			Email people
# 				With default subject
# 				With new subject
# 				With message, plain text
# 				With message, formatting
# 				Without items
# 				With items
# 				With items, when person is not on any.
# 				With contact details
# 				Without contact details
# 				With availability
# 				Without availability
# 404 templates
