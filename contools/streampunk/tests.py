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
from django.core.exceptions import ValidationError
from django.core import mail

from .models import Grid, Gender, Slot, SlotLength, Room
from .models import SlotLength, ConDay, ConInfoBool, ConInfoInt, ConInfoString
from .models import ItemKind, SeatingKind, FrontLayoutKind
from .models import Revision, MediaStatus, ItemPerson, Tag
from .models import PersonStatus, PersonRole, Person, Item
from .models import PersonList, UserProfile
from .models import KitThing, KitRequest, KitBundle, KitRole, KitDepartment
from .models import KitKind, KitStatus, RoomCapacity, KitSource, KitBasis
from .models import KitRoomAssignment, KitItemAssignment, KitSatisfaction
from .models import Check, CheckResult
from .forms import PersonForm
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

  def yesno_link_to(self, yesno, path, args=None):
    return self.has_link_to(path, args) if yesno else self.no_link_to(path, args)

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

  def yesno_column(self, yesno, table, column):
    return self.has_column(table, column) if yesno else self.no_column(table, column)

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

  def yesno_row(self, yesno, table, rec):
    return self.has_row(table, rec) if yesno else self.no_row(table, rec)

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
  def get_tolkien(self):
    return Item.objects.get(shortname='Tolkien panel')
  def get_openingceremony(self):
    return Item.objects.get(shortname='opening ceremony')

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

  def get_greenroomkit(self):
    return KitBundle.objects.get(name='Green room kit')
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

  def zap_avail(self, thing):
    av = list(thing.availability.all())
    for a in av:
      thing.availability.remove(a)

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
    # XXX This still isn't working, and I can't tell why.
    # self.has_link_to('admin:index')
    self.has_link_to('userprofile')
    self.has_link_to('add_kitthing_to_item')
    self.has_link_to('add_kitthing_to_room')
    self.has_link_to('add_kitbundle_to_item')
    self.has_link_to('add_kitbundle_to_room')

  def mkroot(self):
    user = User.objects.create_user(username='congod', password='xxx')
    user.is_superuser = True
    user.email = 'steve@whitecrow.demon.co.uk'
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
    self.assertEqual(self.num_rows(t), 6) # Everywhere, Video, Programme 1 & 2, Main and Second Hall. Ops is not visible
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
    self.assertEqual(self.num_rows(t), 8) # Everywhere, Nowhere, Video, Ops, Main and Second Hall, Programme 1 & 2
    self.has_row(t, { 'name': 'Nowhere', 'visible': False, 'edit': 'Edit', 'remove': 'Remove' })
    self.has_row(t, { 'name': 'Everywhere', 'visible': True, 'edit': 'Edit', 'remove': 'Remove' })
    self.has_link_to('new_room')

  def test_room_listings(self):
    "Check the different types of listing."

    t = 'rtable'
    # Basic listing
    self.response = self.client.get(reverse('list_rooms'))
    self.status_okay()
    self.no_column(t, 'needsSound')
    self.no_column(t, 'privNotes')

    # Programme team listing
    self.response = self.client.get(reverse('list_rooms_prog'))
    self.status_okay()
    self.no_column(t, 'needsSound')
    self.has_column(t, 'privNotes')

    # Tech crew listing
    self.response = self.client.get(reverse('list_rooms_tech'))
    self.status_okay()
    self.has_column(t, 'needsSound')
    self.has_column(t, 'privNotes')

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

    # Check cleaning methods. This needs to be done directly, it seems.

    river_form = PersonForm({
      "firstName":         "  River",
      "middleName":        "\tAssassin ",
      "lastName":          "Tam     ",
      "badge":             "  Death Machine ",
      "email":             "river@bluesun.com",
      "memnum":            666,
      "gender":            Gender.objects.find_default().id,
      "complete":          "No",
      "distEmail":         "No",
      "recordingOkay":     "No"
    })
    self.assertTrue(river_form.is_valid())
    self.assertEqual(river_form.cleaned_data['firstName'], "River")
    self.assertEqual(river_form.cleaned_data['middleName'], "Assassin")
    self.assertEqual(river_form.cleaned_data['lastName'], "Tam")
    self.assertEqual(river_form.cleaned_data['badge'], "Death Machine")

    # Check we can create a user with only one of the three names defined.
    self.response = self.client.post(reverse('new_person'), default_person({
      "firstName":      "foo",
      "middleName":     "",
      "lastName":       ""
    }), follow=True)
    self.status_okay()

    self.response = self.client.post(reverse('new_person'), default_person({
      "firstName":      "",
      "middleName":     "bar",
      "lastName":       ""
    }), follow=True)
    self.status_okay()

    self.response = self.client.post(reverse('new_person'), default_person({
      "firstName":      "",
      "middleName":     "",
      "lastName":       "baz"
    }), follow=True)
    self.status_okay()

    # Check that we object if none of the names is defined.
    # XXX - This is not raising a ValidationError. Why not?
    # with self.assertRaises(ValidationError):
    #   self.response = self.client.post(reverse('new_person'), default_person({
    #     "firstName":      "",
    #     "middleName":     "",
    #     "lastName":       ""
    #   }), follow=True)

    # Check we complain if we say yes to badge-only, but don't set a badge.
    # XXX - This is not raising a ValidationError. Why not?
    # with self.assertRaises(ValidationError):
    #   self.response = self.client.post(reverse('new_person'), default_person({
    #     "firstName":      "Simon",
    #     "lastName":       "Tam",
    #     "badge":          "",
    #     "badge_only":     False
    #   }), follow=True)

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
    chkroom(self, 8) # Main and second halls, Programme 1 & 2, video, ops, everywhere, nowhere
    self.response = self.client.post(reverse('new_room'), {
      "name":        "Foyer",
      "isDefault":   False,
      "isUndefined": False,
      "canClash":    False,
      "visible":     True,
      "gridOrder":   10
    }, follow=True)
    self.status_okay()
    chkroom(self, 9)
    self.has_row(t, { 'name': 'Foyer', 'visible': True, 'edit': 'Edit', 'remove': 'Remove' })

    self.response = self.client.post(reverse('new_room'), {
      "name":        "Green Room",
      "isDefault":   False,
      "isUndefined": False,
      "canClash":    False,
      "gridOrder":   20
    }, follow=True)
    self.status_okay()
    chkroom(self, 10)
    self.has_row(t, { 'name': 'Foyer', 'visible': True,  'edit': 'Edit', 'remove': 'Remove' })
    self.has_row(t, { 'name': 'Green Room',       'visible': False, 'edit': 'Edit', 'remove': 'Remove' })

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


class test_item_listings(AuthTest):
  "Check the right columns appear in the types of listings."

  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_items_normal(self):
    self.response = self.client.get(reverse('list_items'))
    t = 'itable'
    self.has_column(t, 'room')
    self.has_column(t, 'title')
    self.no_column(t, 'projNeeded')
    self.no_column(t, 'satisfies_kit_requests')

  def test_items_tech(self):
    self.response = self.client.get(reverse('list_items_tech'))
    t = 'itable'
    self.has_column(t, 'room')
    self.has_column(t, 'title')
    self.has_column(t, 'projNeeded')
    self.has_column(t, 'satisfies_kit_requests')

# =========================================================


class test_add_panellists(AuthTest):
  "Adding people to items."
  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_people_items(self):
    buffy = self.get_buffy()		# Is on Disco
    giles = self.get_giles()		# Is on Tolkien, Cabaret and Art auction
    ceilidh = self.get_ceilidh()	# Has Jayne and Simon
    disco = self.get_disco()		# Has Buffy,  River and Dawn
    panellist = PersonRole.objects.find_default()
    
    itable = 'item_people_table'  # people on the item
    ptable = 'person_items_table' # items person is on

    # Buffy is on the disco, but nothing else
    self.response = self.client.get(reverse('show_person_detail', kwargs={ "pk": buffy.id }))
    self.status_okay()
    self.assertEqual(self.num_rows(ptable), 1)
    self.has_row(ptable, { "item": disco, "role": panellist })

    # Disco has Buffy, River and Dawn.
    self.response = self.client.get(reverse('show_item_detail', kwargs={ "pk": disco.id }))
    self.status_okay()
    self.has_row(itable, { "person": buffy, "role": panellist, "visible": True })

    # Add Giles to the ceilidh, so it'll be Giles, Jayne and Simon
    # And Giles will be on ceilidh, Tolkein, art auction and cabaret

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

    # Add Buffy to the ceilidh, so that it'll have Jayne, Simon, Giles and Buffy,
    # and buffy will be on ceilidh and disco

    self.response = self.client.post(reverse('new_itemperson'), default_itemperson({
      "item":    ceilidh.id,
      "person":  buffy.id,
      "role":    panellist.id
    }), follow=True)
    self.status_okay()

    # Add Giles to disco, so that he's on disco, cabaret, ceilidh, tolkien, art auction
    # and Disco will have buffy, giles, dawn, river.

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
    self.assertEqual(self.num_rows(itable), 4) # giles, buffy, Jayne and Simon
    self.has_row(itable, { "person": buffy, "role": panellist, "visible": True })
    self.has_row(itable, { "person": giles, "role": panellist, "visible": True })

    self.response = self.client.get(reverse('show_person_detail', kwargs={ "pk": giles.id }))
    self.status_okay()
    self.assertEqual(self.num_rows(ptable), 5) # disco, cabaret, ceilidh, tolkien, art auction
    self.has_row(ptable, { "item": disco, "role": panellist, "visible": True })
    self.has_row(ptable, { "item": ceilidh, "role": panellist, "visible": True })

    self.response = self.client.get(reverse('show_item_detail', kwargs={ "pk": disco.id }))
    self.status_okay()
    self.assertEqual(self.num_rows(itable), 4) # buffy, giles, dawn, river.
    self.has_row(itable, { "person": giles, "role": panellist, "visible": True })
    self.has_row(itable, { "person": buffy, "role": panellist, "visible": True })

    # Add Giles to the disco, which he's already on.

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
    self.assertEqual(self.num_rows(itable), 4) # buffy, giles, dawn, river.
    self.has_row(itable, { "person": buffy, "role": panellist, "visible": True })
    
    # But a POST should work.
    self.response = self.client.post(reverse('delete_itemperson', kwargs={ "pk": ip.id }), {
      "after": reverse('show_item_detail', kwargs={ "pk": disco.id })
    },  follow=True)
    self.status_okay()
    self.response = self.client.get(reverse('show_item_detail', kwargs={ "pk": disco.id }))
    self.status_okay()
    self.assertEqual(self.num_rows(itable), 3) # giles, dawn, river.
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

    # Clear out the tags on Giles
    tags = giles.tags.all()
    for t in tags:
      giles.tags.remove(t)
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
    person_lists_tags(self, giles, [ ])

    # Again, but with only one new tag.
    # Looks like this particular test currently fails.
    newtags = [ books ]
    self.response = self.client.post(reverse('edit_tags_for_person', args=[ buffy.id ]), {
      "tags": tagids(newtags)
    }, follow=True)
    self.status_okay()
    person_lists_tags(self, buffy, newtags)
    person_lists_tags(self, giles, [ ])

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
  fixtures = [ 'demo_data' ]

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
  fixtures = [ 'demo_data' ]

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
    tolkien = self.get_tolkien()
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
    self.assertEqual(tolkien.tags.count(), 2)
    delpath = reverse('delete_item', kwargs={'pk': tolkien.id})
    self.response = self.client.post(delpath, { }, follow=True)
    self.status_okay()
    self.assertFalse(Item.objects.filter(shortname='Tolkien panel').exists())

    # Check that it's okay to delete an item that has people on it.

    delpath = reverse('delete_item', kwargs={'pk': ceilidh.id})
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

    # Clear out what's currently there
    KitRequest.objects.all().delete()
    KitItemAssignment.objects.all().delete()

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
  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_delete_tags_on_stuff(self):
    "Test deleting tags, on people and items."
    xander = self.get_xander()		# comics, buffy, fandom, star trek
    tolkien = self.get_tolkien()	# books, fantasy
    books = self.get_books()		# Giles, Tolkein
    movies = self.get_movies()		# Nothing
    comics = self.get_comics()		# Xander

    self.assertEqual(books.item_set.count(), 1)
    self.assertEqual(books.person_set.count(), 1)
    self.assertEqual(movies.item_set.count(), 0)
    self.assertEqual(movies.person_set.count(), 0)
    self.assertEqual(comics.item_set.count(), 0)
    self.assertEqual(comics.person_set.count(), 1)
    self.assertTrue(xander in comics.person_set.all())
    self.assertTrue(tolkien in books.item_set.all())
    self.assertEqual(xander.tags.count(), 4)
    self.assertEqual(tolkien.tags.count(), 2)
    self.assertTrue(books in tolkien.tags.all())
    self.assertTrue(comics in xander.tags.all())

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
    self.assertEqual(xander.tags.count(), 3)
    self.assertEqual(tolkien.tags.count(), 1)

# =========================================================

class test_delete_rooms(AuthTest):
  "Deleting rooms"
  fixtures = [ 'demo_data' ]

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

    # Make the video room the default room
    video.isDefault = True
    video.save()
    nowhere.isDefault = False
    nowhere.save()

    # we can delete the Main Hall
    self.response = self.client.post(reverse('delete_room', args=[ mainhall.id ]), { }, follow=True)
    self.status_okay()
    self.assertFalse(Room.objects.filter(name='Main Hall').exists())

    # But all those items should still exist, now in Nowhere, as it is
    # the 'undefined' room.
    for i in mh_item_ids:
      self.assertTrue(Item.objects.filter(id=i, room=nowhere).exists())

    # We should get an assertion if we try to delete nowhere, though, because
    # it's the 'undefined' room.
    with self.assertRaises(DeleteUndefException):
      self.client.post(reverse('delete_room', args=[ nowhere.id ]), { })
    self.assertTrue(Room.objects.filter(name='Nowhere').exists())

    # Equally, we should get an assertion if we try to delete the video room,
    # as it's currently the default room.
    with self.assertRaises(DeleteDefaultException):
      self.client.post(reverse('delete_room', args=[ video.id ]), { })
    self.assertTrue(Room.objects.filter(name='Video').exists())

    # Change Nowhere back to being the default room again.
    video.isDefault = False
    video.save()
    nowhere.isDefault = True
    nowhere.save()

    # There is a capacity attached to the video room
    self.assertEqual(video.capacities.count(), 1)
    cap1 = video.capacities.all()[0]
    cap1id = cap1.id

    # It's used by Programme 2, too.
    self.assertEqual(cap1.room_set.count(), 2)

    # Delete the Video room.
    self.response = self.client.post(reverse('delete_room', args=[ video.id ]), { }, follow=True)
    self.status_okay()

    self.assertFalse(Room.objects.filter(name='Video').exists())

    # Currently, we expect the capacity object to still exist

    self.assertTrue(RoomCapacity.objects.filter(id=cap1id).exists())
    cap1 = RoomCapacity.objects.get(id=cap1id)
    self.assertEqual(cap1.room_set.count(), 1)  # Just Programme 2 now

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

    # Clear out the room assignments
    KitRoomAssignment.objects.all().delete()

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
  fixtures = [ 'demo_data' ]

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
    disco = self.get_disco()
    ceilidh = self.get_ceilidh()

    mod = PersonRole.objects.get(name='Moderator')
    speaker = PersonRole.objects.get(name='Speaker')
    panellist = self.get_panellist()

    invited = PersonStatus.objects.get(name='Invited')
    confirmed = PersonStatus.objects.get(name='Confirmed')

    # Make sure we don't currently have any uses of these statuses
    self.assertEqual(ItemPerson.objects.filter(status=invited).count(), 0)
    self.assertEqual(ItemPerson.objects.filter(status=confirmed).count(), 0)
    self.assertEqual(ItemPerson.objects.filter(role=mod).count(), 0)
    self.assertEqual(ItemPerson.objects.filter(role=speaker).count(), 0)

    # We'll delete Moderator, leave Speaker untouched.
    discopeeps = ItemPerson.objects.filter(item=disco)
    discopeeps.update(role=mod, status=confirmed)

    # We'll delete Proposed, and leave Confirmed untouched.
    ceilidhpeeps = ItemPerson.objects.filter(item=ceilidh)
    ceilidhpeeps.update(role=speaker, status=invited)

    # PersonRole
    # Choice of 4+, everything TBA

    self.poke_enum(all=ItemPerson.objects.all(),
                   should_change=discopeeps,
                   change_from=mod,
                   change_to=PersonRole.objects.find_undefined(),
                   matches=(lambda thing, val: thing.role==val))

    # PersonStatus
    # Several choices, all TBA

    self.poke_enum(all=ItemPerson.objects.all(),
                   should_change=ceilidhpeeps,
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
  fixtures = [ 'demo_data' ]

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

    disco = self.get_disco()	# No tags
    editurl = reverse('edit_tags_for_item', args=[ disco.id ])
    books = self.get_books()	# Has Tolkien, giles
    movies = self.get_movies()	# Nothing

    # Check that there's no tags on the item yet
    self.assertEqual(disco.tags.count(), 0)
    # Check existing uses of the tags
    self.assertEqual(books.item_set.count(), 1)   # For Tolkien
    self.assertEqual(movies.item_set.count(), 0)  # Nothing

    # Check that the item doesn't appear in a search on the tags
    tag_lists_item(self, books, disco, False)
    tag_lists_item(self, movies, disco, False)
    # And that the item doesn't list the tags
    item_lists_tag(self, disco, books, False)
    item_lists_tag(self, disco, movies, False)

    # Add one of the tags to the item. Books will list Tolkien, disco
    self.response = self.client.post(editurl, { "tags": [ books.id ] }, follow=True)
    self.status_okay()
    self.form_okay()

    # Check that the item now lists books, but not movies.
    tag_lists_item(self, books, disco, True)
    tag_lists_item(self, movies, disco, False)
    # And that the item lists only books
    item_lists_tag(self, disco, books, True)
    item_lists_tag(self, disco, movies, False)
    self.assertEqual(disco.tags.count(), 1)		# Just books
    self.assertEqual(books.item_set.count(), 2)		# disco and tolkien
    self.assertEqual(movies.item_set.count(), 0)	# nothing

    # Add movies, too. So disco will will have books and movies
    self.response = self.client.post(editurl, { "tags": [ books.id, movies.id ] }, follow=True)
    self.status_okay()
    self.form_okay()

    # Check that the item now lists both books and movies.
    tag_lists_item(self, books, disco, True)
    tag_lists_item(self, movies, disco, True)
    # And that the item lists only books
    item_lists_tag(self, disco, books, True)
    item_lists_tag(self, disco, movies, True)
    self.assertEqual(disco.tags.count(), 2)		# books and movies
    self.assertEqual(books.item_set.count(), 2)		# disco and tolkien
    self.assertEqual(movies.item_set.count(), 1)	# disco

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
    self.assertEqual(disco.tags.count(), 1)		# movies
    self.assertEqual(books.item_set.count(), 1)		# tolkien
    self.assertEqual(movies.item_set.count(), 1)	# disco

    # Edit again, to have no tags.
    self.response = self.client.post(editurl, { }, follow=True)
    self.status_okay()
    self.form_okay()

    tag_lists_item(self, books, disco, False)
    tag_lists_item(self, movies, disco, False)
    # And that the item doesn't list the tags
    item_lists_tag(self, disco, books, False)
    item_lists_tag(self, disco, movies, False)
    self.assertEqual(disco.tags.count(), 0)		# Nothing
    self.assertEqual(books.item_set.count(), 1)		# tolkien
    self.assertEqual(movies.item_set.count(), 0)	# nothing

    # Edit to include books twice; check that we don't get two instances.
    self.response = self.client.post(editurl, { "tags": [ books.id, books.id ] }, follow=True)
    self.status_okay()
    self.form_okay()

    tag_lists_item(self, books, disco, True)
    tag_lists_item(self, movies, disco, False)
    item_lists_tag(self, disco, books, True)
    item_lists_tag(self, disco, movies, False)
    self.assertEqual(disco.tags.count(), 1)		# books
    self.assertEqual(books.item_set.count(), 2)		# disco, tolkien
    self.assertEqual(movies.item_set.count(), 0)	# nothing

  def test_edit_kit_requests(self):
    "Change kit requests on an item."

    disco = self.get_disco()

    # No kit requests on disco yet
    self.assertEqual(disco.kitRequests.count(), 0)
    prev_reqs = list(KitRequest.objects.all())

    self.response = self.client.post(reverse('add_kitrequest_to_item', args=[ disco.id ]), {
      "kind": KitKind.objects.find_default().id,
      "count": 1,
      "setupAssistance": False,
      "status": KitStatus.objects.find_default().id
    }, follow=True)
    self.status_okay()
    self.form_okay()
    self.assertEqual(disco.kitRequests.count(), 1)

    # Let's see which one it is.
    for kr in KitRequest.objects.all():
      if kr not in prev_reqs:
        req = kr
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
    self.assertEqual(KitRequest.objects.count(), len(prev_reqs))

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
  fixtures = [ 'demo_data' ]

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
  
    self.assertEqual(len(disco.kit_item_assignments()), 0)

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
    self.assertTrue(kiaproj2 in disco.kit_item_assignments())
    self.assertTrue(disco.has_unsatisfied_kit_requests())
    self.assertFalse(disco.satisfies_kit_requests())

    # Assign the larger request to an item as well. Should now be enough.
    kiaproj4 = KitItemAssignment(item=disco, thing=ktproj4)
    kiaproj4.save()
    self.assertTrue(kiaproj4 in disco.kit_item_assignments())
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
  fixtures = [ 'demo_data' ]

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
    self.assertTrue(kraproj2 in disco.kit_room_assignments())
  
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
    self.assertTrue(kraproj2 in disco.kit_room_assignments())
    self.assertTrue(kraproj4 in disco.kit_room_assignments())

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

  def test_kit_bundle_in_use(self):
    "Check that a kit bundle is in use if it's on an item or in a room."
    green = self.get_greenroomkit()
    main = self.get_mainhallkit()

    # Green's already used by an item and by a room.
    self.assertTrue(green.in_use())
    self.assertTrue(green.item_count() > 0)
    self.assertTrue(green.room_count() > 0)

    # Main's used by a room, but not by an item.
    self.assertTrue(main.in_use())
    self.assertTrue(main.item_count() == 0)
    self.assertTrue(main.room_count() > 0)

    # Stop Green being used by a room, so it's only used by an item.
    KitRoomAssignment.objects.filter(bundle=green).delete()
    green = self.get_greenroomkit()
    self.assertTrue(green.item_count() > 0)
    self.assertTrue(green.room_count() == 0)
    self.assertTrue(green.in_use())

    # Stop Green being used by an item, too. That should make it
    # no longer in use.
    KitItemAssignment.objects.filter(bundle=green).delete()
    green = self.get_greenroomkit()
    self.assertTrue(green.item_count() == 0)
    self.assertTrue(green.room_count() == 0)
    self.assertFalse(green.in_use())


# =========================================================

class test_overlaps(AuthTest):
  "Check whether things overlap properly."
  fixtures = [ 'demo_data' ]

  def test_item_overlaps(self):
    disco = self.get_disco()		# two-hour slot
    ceilidh = self.get_ceilidh()	# one-hour slot

    # grab a couple of adjacent slots
    friday9pm = Slot.objects.get(startText='9pm', day__name='Friday')
    friday10pm = Slot.objects.get(startText='10pm', day__name='Friday')

    # These don't overlap each other, yet.
    self.assertFalse(disco.overlaps(ceilidh))
    self.assertFalse(ceilidh.overlaps(disco))
    # and nothing should overlap itself.
    self.assertFalse(disco.overlaps(disco))
    self.assertFalse(ceilidh.overlaps(ceilidh))

    # Move them both to the same slot. They should overlap.
    disco.start = friday9pm
    disco.save()
    ceilidh.start = friday9pm
    ceilidh.save()

    self.assertTrue(disco.overlaps(ceilidh))
    self.assertTrue(ceilidh.overlaps(disco))

    # Move the disco to the later slot.
    disco.start = friday10pm
    disco.save()

    # should no longer overlap, because the shorter item is first.
    self.assertFalse(disco.overlaps(ceilidh))
    self.assertFalse(ceilidh.overlaps(disco))
     
    # Swap them around. They should now overlap, because the two-hour item is first.
    disco.start = friday9pm
    disco.save()
    ceilidh.start = friday10pm
    ceilidh.save()
    self.assertTrue(disco.overlaps(ceilidh))
    self.assertTrue(ceilidh.overlaps(disco))

# =========================================================

class test_satisfaction(AuthTest):
  "Satisfying Kit Requests."
  fixtures = [ 'demo_data' ]

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

    # Clear out any kit assignments from the item, and the item's room
    self.assertEqual(disco.kitRequests.count(), 0)
    self.assertEqual(disco.kit.count(), 0)
    self.assertNotEqual(disco.room.kit.count(), 0)
    KitRoomAssignment.objects.filter(room=disco.room).delete()
    self.assertEqual(disco.room.kit.count(), 0)

    req = self.req_proj()
    self.add_req_to_item(req, disco)
    self.assertEqual(disco.kitRequests.count(), 1)
    # convert our dict back into the proper request
    req = disco.kitRequests.all()[0]

    # There's no KitThing on this item that satisfies the request.
    # Nor is there a KitThing on the room that satisfies it.

    # Check directly
    self.assertFalse(disco.satisfies_kit_requests())
    self.assertTrue(disco.has_unsatisfied_kit_requests())
    ks = KitSatisfaction(disco)
    self.assertFalse(ks.satisfied)
    missing = ks.missing_things()
    self.assertEqual(len(missing), 1)
    self.assertEqual(missing[0][0], self.get_proj())
    self.assertEqual(missing[0][1], 1)

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

class test_kitreq_listings(AuthTest):
  "Check the listing of kit requests"

  def test_list_kit_reqs(self):
    "Fetch the kit requests."

    kitreqs = KitRequest.objects.all()
    self.response = self.client.get(reverse('list_kitrequests'))
    self.assertEqual(self.num_rows('krtable'), kitreqs.count())
    for kr in kitreqs:
      self.has_link_to(kr.get_absolute_url())

class test_kit_add(AuthTest):
  "Fetch the forms wherein we add kit to stuff."

  fixtures = [ 'demo_data' ]

  def test_fetch_kr_to_item(self):
    disco = self.get_disco()
    self.response = self.client.get(reverse('add_kitrequest_to_item', args=[int(disco.id)]))
    self.status_okay()
    self.form_okay()

  def test_fetch_kb_to_item(self):
    disco = self.get_disco()
    greenroomkit = self.get_greenroomkit()
    self.response = self.client.get(reverse('add_kitbundle_to_item') , { "item": int(disco.id)})
    self.status_okay()
    self.form_okay()
    self.response = self.client.get(reverse('add_kitbundle_to_item') , { "bundle": int(greenroomkit.id)})
    self.status_okay()
    self.form_okay()

  def test_fetch_kb_to_room(self):
    video = self.get_video()
    greenroomkit = self.get_greenroomkit()
    self.response = self.client.get(reverse('add_kitbundle_to_room'), { "room": int(video.id)})
    self.status_okay()
    self.form_okay()
    self.response = self.client.get(reverse('add_kitbundle_to_room') , { "bundle": int(greenroomkit.id)})
    self.status_okay()
    self.form_okay()

  def test_fetch_kt_to_item(self):
    disco = self.get_disco()
    greenroomscr = self.get_greenroomscr()
    self.response = self.client.get(reverse('add_kitthing_to_item') , { "item": int(disco.id)})
    self.status_okay()
    self.form_okay()
    self.response = self.client.get(reverse('add_kitthing_to_item') , { "thing": int(greenroomscr.id)})
    self.status_okay()
    self.form_okay()

  def test_fetch_kt_to_room(self):
    video = self.get_video()
    greenroomscr = self.get_greenroomscr()
    self.response = self.client.get(reverse('add_kitthing_to_room'), { "room": int(video.id)})
    self.status_okay()
    self.form_okay()
    self.response = self.client.get(reverse('add_kitthing_to_room') , { "thing": int(greenroomscr.id)})
    self.status_okay()
    self.form_okay()

# =========================================================

class test_room_availability(AuthTest):
  "Direct test of room availability."
  fixtures = [ 'demo_data' ]

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

    self.zap_avail(room)

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
  fixtures = [ 'demo_data' ]

  def test_never_and_always(self):

    # Get some people to play with
    buffy = self.get_buffy()
    giles = self.get_giles()

    self.zap_avail(buffy)
    self.zap_avail(giles)

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
  fixtures = [ 'demo_data' ]

  def test_never_and_always(self):

    # Get some stuff to play with
    proj = self.get_greenroomproj()
    screen = self.get_greenroomscr()

    self.zap_avail(proj)
    self.zap_avail(screen)

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

    self.zap_avail(proj)

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

    # Clean out the availability on each
    self.zap_avail(ops)
    self.zap_avail(proj)

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
  fixtures = [ 'demo_data' ]

  def test_starting_direct(self):
    """
    Check that a slot knowns the difference between 'item occupies slot'
    and 'item starts in slot'.
    """
    # Snarf the usual items
    disco = self.get_disco()
    cabaret = self.get_cabaret()
    ceilidh = self.get_ceilidh()

    cabaret_slot = Slot.objects.get(startText='9pm', day__name='Friday')
    disco_slot = Slot.objects.get(startText='10pm', day__name='Friday')
    cabaret.start = cabaret_slot
    cabaret.save()
    disco.start = disco_slot
    disco.save()

    self.assertEqual(cabaret_slot, cabaret.start)
    self.assertEqual(disco_slot, disco.start)
    self.assertEqual(disco_slot, ceilidh.start)

    for i in [ disco, cabaret, ceilidh ]:
      self.assertTrue(i in disco_slot.items())
    for i in [ ceilidh, disco ]:
      self.assertTrue(i in disco_slot.items_starting())
      self.assertFalse(i in cabaret_slot.items_starting())
      self.assertFalse(i in cabaret_slot.items())

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

    cabaret_slot = Slot.objects.get(startText='9pm', day__name='Friday')
    disco_slot = Slot.objects.get(startText='10pm', day__name='Friday')

    cabaret.start = cabaret_slot
    cabaret.save()
    disco.start = disco_slot
    disco.save()


    # Check what appears in the items and items_starting lists for each slot.
    # No room specified yet.
    # We expect:
    # 9pm: items: cabaret
    # 9pm starting: cabaret
    # 10pm: items: disco, cabaret, ceilidh
    # 10pm: starting: disco, ceilidh

    self.response = self.client.get(reverse('show_slot_detail', args=[cabaret_slot.id]))
    self.status_okay()
    self.has_row('itable', { "title": cabaret.title })
    self.has_row('itable_starting', { "title": cabaret.title })
    self.no_row('itable', { "title": disco.title })
    self.no_row('itable_starting', { "title": disco.title })
    self.no_row('itable', { "title": ceilidh.title })
    self.no_row('itable_starting', { "title": ceilidh.title })

    self.response = self.client.get(reverse('show_slot_detail', args=[disco_slot.id]))
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
      self.assertTrue(i in disco_slot.items())
    for i in [ disco, ceilidh ]:
      self.assertTrue(i in disco_slot.items_starting())
      self.assertFalse(i in cabaret_slot.items_starting())
      self.assertFalse(i in cabaret_slot.items())
    self.assertTrue(cabaret in cabaret_slot.items())
    self.assertTrue(cabaret in cabaret_slot.items_starting())

    # We expect:
    # 9pm main hall: items: cabaret
    # 9pm main hall starting: cabaret
    # 10pm main hall: items: cabaret, ceilidh
    # 10pm main hall: starting: ceilidh

    rm = cabaret.room
    self.assertTrue(cabaret in cabaret_slot.items(rm))
    self.assertTrue(cabaret in cabaret_slot.items_starting(rm))
    for i in [ disco, ceilidh ]:
      self.assertFalse(i in cabaret_slot.items_starting(rm))
      self.assertFalse(i in cabaret_slot.items(rm))
    for i in [ cabaret, ceilidh ]:
      self.assertTrue(i in disco_slot.items(rm))
    self.assertTrue(ceilidh in disco_slot.items_starting(rm))
    self.assertFalse(cabaret in disco_slot.items_starting(rm))
    self.assertFalse(disco in disco_slot.items_starting(rm))
    self.assertFalse(disco in disco_slot.items(rm))

    # We expect:
    # 9pm ops: items: nothing
    # 9pm ops starting: nothing
    # 10pm ops: items: disco
    # 10pm ops: starting: disco

    for i in [ disco, cabaret, ceilidh ]:
      self.assertFalse(i in cabaret_slot.items(ops))
      self.assertFalse(i in cabaret_slot.items_starting(ops))
    for i in [ cabaret, ceilidh ]:
      self.assertFalse(i in disco_slot.items(ops))
      self.assertFalse(i in disco_slot.items_starting(ops))
    self.assertTrue(disco in disco_slot.items(ops))
    self.assertTrue(disco in disco_slot.items_starting(ops))

class test_grids(AuthTest):
  "Direct test of what appears in grid cells."
  fixtures = [ 'demo_data' ]

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
    ceilidh = self.get_bidsession()

    buffy = self.get_buffy()
    giles = self.get_giles()
    dawn = self.get_dawn()

    # XXX There's a question of a bug here. If we make an item non-visible,
    # should that make us treat all the people as non-visible too, regardless
    # of how they've been added? Should we just make that a Check?
    ceilidh.visible = False
    ceilidh.save()

    self.assertTrue(disco.visible)
    self.assertTrue(cabaret.visible)
    self.assertFalse(ceilidh.visible)

    # Add each of the people to each of the items, but mix-and-match
    # who should be visible on each.

    # buffy and dawn are already on the disco, and visible
    ip = ItemPerson(item=cabaret, person=buffy, visible=True)
    ip.save()
    ip = ItemPerson(item=ceilidh, person=buffy, visible=True)
    ip.save()
    # Giles is on the cabaret - make him invisible
    ItemPerson.objects.filter(item=cabaret, person=giles).update(visible=False)
    ip = ItemPerson(item=disco, person=giles, visible=False)
    ip.save()
    ip = ItemPerson(item=ceilidh, person=giles, visible=False)
    ip.save()
    ip = ItemPerson(item=cabaret, person=dawn, visible=True)
    ip.save()
    ip = ItemPerson(item=ceilidh, person=dawn, visible=False)
    ip.save()

    # Everyone should all be returned by the people lists, because they don't filter.

    for p in [ buffy, giles, dawn ]:
      for i in [ disco, cabaret, ceilidh ]:
        self.assertTrue(p in i.people.all())

    # Buffy should also be in the public list for each item, but Giles should not be.

    for i in [ disco, cabaret, ceilidh ]:
      self.assertTrue(buffy in i.people_public())
      self.assertFalse(giles in i.people_public())

    # Dawn should be in the public list for disco and cabaret, but not the big session.
    self.assertTrue(dawn in disco.people_public())
    self.assertTrue(dawn in cabaret.people_public())
    self.assertFalse(dawn in ceilidh.people_public())

class test_grids_public(NonauthTest):
  "Test what the templates retrieve, for grids."
  fixtures = [ 'demo_data' ]

  def test_people_on_items_in_cells(self):
    "Check that people are visible on items in cells (or not)."

    disco = self.get_disco()
    cabaret = self.get_cabaret()
    ceilidh = self.get_ceilidh()

    buffy = self.get_buffy()
    giles = self.get_giles()
    dawn = self.get_dawn()

    ceilidh.visible = False
    ceilidh.save()

    self.assertTrue(disco.visible)
    self.assertTrue(cabaret.visible)
    self.assertFalse(ceilidh.visible)

    # Move each of these items to 11am, on consecutive days

    disco.start = Slot.objects.get(startText='11am', day__name='Friday')
    disco.save()
    cabaret.start = Slot.objects.get(startText='11am', day__name='Saturday')
    cabaret.save()
    ceilidh.start = Slot.objects.get(startText='11am', day__name='Sunday')
    ceilidh.save()

    # Add each of the people to each of the items, but mix-and-match
    # who should be visible on each.

    # Buffy and Dawn are already on the disco, and visible
    ip = ItemPerson(item=cabaret, person=buffy, visible=True)
    ip.save()
    ip = ItemPerson(item=ceilidh, person=buffy, visible=True)
    ip.save()
    ip = ItemPerson(item=disco, person=giles, visible=False)
    ip.save()
    # Giles is already on the cabaret, but visible - change that
    ItemPerson.objects.filter(item=cabaret, person=giles).update(visible=False)
    ip = ItemPerson(item=ceilidh, person=giles, visible=False)
    ip.save()
    ip = ItemPerson(item=cabaret, person=dawn, visible=True)
    ip.save()
    ip = ItemPerson(item=ceilidh, person=dawn, visible=False)
    ip.save()

    # Everyone but Giles should be visible, for the disco

    grid = Grid.objects.get(name='Friday 10am-2pm')
    self.assertTrue(disco.start in grid.slots.all())
    self.response = self.client.get(reverse('show_grid', kwargs={ "gr": grid.id }))
    self.status_okay()
    self.has_link_to('show_item_detail', args=[int(disco.id)])
    self.has_link_to('show_person_detail', args=[int(buffy.id)])
    self.has_link_to('show_person_detail', args=[int(dawn.id)])
    self.no_link_to('show_person_detail', args=[int(giles.id)])

    # Buffy and Dawn are visible on the cabaret, but Giles is not.

    grid = Grid.objects.get(name='Saturday 10am-2pm')
    self.assertTrue(cabaret.start in grid.slots.all())
    self.response = self.client.get(reverse('show_grid', kwargs={ "gr": grid.id }))
    self.status_okay()
    self.has_link_to('show_item_detail', args=[int(cabaret.id)])
    self.has_link_to('show_person_detail', args=[int(buffy.id)])
    self.has_link_to('show_person_detail', args=[int(dawn.id)])
    self.no_link_to('show_person_detail', args=[int(giles.id)])

    # The bid session isn't visible, so we shouldn't see it, or anyone on it.

    grid = Grid.objects.get(name='Sunday 10am-2pm')
    self.assertTrue(ceilidh.start in grid.slots.all())
    self.response = self.client.get(reverse('show_grid', kwargs={ "gr": grid.id }))
    self.status_okay()
    self.no_link_to('show_item_detail', args=[int(ceilidh.id)])
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

class test_xml_public(NonauthTest):
  "Pull the XML dump down, and see what's in there, but as a non-authenticated person."

  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.client = Client()

  def test_rooms(self):
    "Check all the visible rooms are listed."

    self.response = self.client.get(reverse('xml_dump'))
    self.status_okay()
    for room in Room.objects.filter(visible=True):
      self.assertTrue(room.name in self.response.content)
    for room in Room.objects.exclude(visible=True):
      self.assertFalse(room.name in self.response.content)

  def test_people(self):
    "Check all the people are listed, by badge name."

    self.response = self.client.get(reverse('xml_dump'))
    self.status_okay()
    for person in Person.objects.all():
      if person.as_name() != person.as_badge():
        # If their name doesn't match their badge, we shouldn't see their name.
        self.assertFalse(person.as_name() in self.response.content)
      self.assertTrue(person.as_badge() in self.response.content)

  def test_items(self):
    "Check all the visible items are listed, if they're in a visible room."

    self.response = self.client.get(reverse('xml_dump'))
    self.status_okay()
    for item in Item.scheduled.filter(visible=True):
      self.assertTrue(escape(item.title) in self.response.content)
      self.assertTrue(escape(item.shortname) in self.response.content)
    for item in Item.scheduled.exclude(visible=True):
      # Checking item is omitted as item is not visible
      self.assertFalse(escape(item.title) in self.response.content)
      self.assertFalse(escape(item.shortname) in self.response.content)
    for item in Item.scheduled.exclude(room__visible=True):
      # Checking item is omitted as item's room is not visible
      self.assertFalse(escape(item.title) in self.response.content)
      self.assertFalse(escape(item.shortname) in self.response.content)
    for item in Item.unscheduled.all():
      # Checking item is omitted as item is not scheduled
      self.assertFalse(escape(item.title) in self.response.content)
      self.assertFalse(escape(item.shortname) in self.response.content)


class test_xml(AuthTest):
  "Pull the XML dump down, and see what's in there."

  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_rooms(self):
    "Check all the rooms are listed."

    # Include some room capacities, so that that gets exercised too.

    empty = self.get_empty()
    theatre = self.get_theatre()
    mainhall = self.get_mainhall()
    video = self.get_video()

    empty_hall = RoomCapacity(layout = empty, count = 60)
    empty_hall.save()
    mainhall.capacities.add(empty_hall)
    theatre_hall = RoomCapacity(layout = theatre, count = 50)
    theatre_hall.save()
    mainhall.capacities.add(theatre_hall)
    empty_video = RoomCapacity(layout = empty, count = 42)
    empty_video.save()
    video.capacities.add(empty_video)

    self.response = self.client.get(reverse('xml_dump'))
    self.status_okay()
    for room in Room.objects.all():
      self.assertTrue(room.name in self.response.content)
      for cap in room.capacities.all():
        self.assertTrue(cap.as_xml() in self.response.content)

  def test_people(self):
    "Check all the people are listed."

    self.response = self.client.get(reverse('xml_dump'))
    self.status_okay()
    for person in Person.objects.all():
      self.assertTrue(person.as_name() in self.response.content)
      self.assertTrue(person.as_badge() in self.response.content)

  def test_items(self):
    "Check the scheduled items are listed, and the unscheduled ones are not."

    self.response = self.client.get(reverse('xml_dump'))
    self.status_okay()
    for item in Item.scheduled.all():
      self.assertTrue(escape(item.title) in self.response.content)
      self.assertTrue(escape(item.shortname) in self.response.content)
    for item in Item.unscheduled.all():
      self.assertFalse(escape(item.title) in self.response.content)
      self.assertFalse(escape(item.shortname) in self.response.content)

  def test_kit(self):
    "Check that kit turns up in the XML dump."

    # Note which kit things are assigned to items or rooms

    assigned_to_items = [ kia.thing for kia in KitItemAssignment.objects.all() ]
    assigned_to_rooms = [ kra.thing for kra in KitRoomAssignment.objects.all() ]
    assigned_things = assigned_to_items + assigned_to_rooms
    self.response = self.client.get(reverse('xml_dump'))
    self.status_okay()
    for kt in KitThing.objects.all():
      if kt in assigned_things:
        self.assertTrue(kt.as_xml() in self.response.content)
      else:
        self.assertFalse(kt.as_xml() in self.response.content)
    for kr in KitRequest.objects.all():
      self.assertTrue(kr.as_xml() in self.response.content)

class test_unicode_and_urls(AuthTest):
  "Prod the unicode/get-abs-url methods of classes where that's not normally exercised."

  fixtures = [ 'demo_data' ]
  unicodes = [ KitItemAssignment, KitRoomAssignment, Check, PersonList, UserProfile, RoomCapacity ]
  xxx_urls = [ KitItemAssignment, KitRoomAssignment, Check, PersonList, UserProfile ]
  fetchable = [ KitItemAssignment, KitRoomAssignment, Check, PersonList ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_unicode(self):
    for cls in self.unicodes:
      for obj in cls.objects.all():
        self.assertEqual(str(obj), obj.__unicode__())
  def test_url(self):
    for cls in self.xxx_urls:
      for obj in cls.objects.all():
        self.assertTrue(obj.get_absolute_url())
  def test_fetchable(self):
    for cls in self.fetchable:
      for obj in cls.objects.all():
        self.response = self.client.get(obj.get_absolute_url())
        self.status_okay()

class test_shortnames(AuthTest):
  "Check how we render shortnames"

  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_items_wo_title(self):
    disco = self.get_disco()
    ceilidh = self.get_ceilidh()
    disco.title = ""
    disco.save()
    ceilidh.save()

    for i in Item.objects.all():
      self.assertEqual(str(i), i.__unicode__())
    self.response = self.client.get(reverse('list_items'))
    self.status_okay()

class test_person_as_badge(NonauthTest):
  "Test that we see the name rendered as a badge."

  fixtures = [ 'demo_data' ]

  def test_name_as_badge(self):
    self.response = self.client.get(reverse('list_people'))
    self.status_okay()
    t = 'ptable'
    self.has_column(t, 'name')
    self.has_column(t, 'badge')
    for p in Person.objects.all():
      self.has_row(t, { 'badge': p.badge } )
      if p.badge_only:
        self.has_row(t, { 'name': p.as_badge() } )
        self.no_row(t, { 'name': p.as_name() } )
      else:
        self.has_row(t, { 'name': p.as_name() } )

  def test_itempeople_as_badge(self):
    "Check that names are hidden, when displayed on items."

    dawn = self.get_dawn()
    disco = self.get_disco()
    self.assertTrue(dawn.badge_only)
    self.assertTrue(dawn in disco.people.all())
    self.response = self.client.get(reverse('show_item_detail', args=[int(disco.id)]))
    self.status_okay()
    t = 'item_people_table'
    self.has_column(t, 'badge')
    self.no_column(t, 'name')
    self.has_row(t, { 'badge': dawn.as_badge() } )

# -----------------------------------------------------------------------------------

class PermTest(AuthTest):
  "For tests relating to permissions and groups."

  def can_read_private(self, yesno):
    "yesno says whether we're expected to be able to read private data."

    self.assertEqual(yesno, self.rootuser.has_perm('streampunk.read_private'))
    self.response = self.client.get(reverse('list_people'))
    self.status_okay()
    t = 'ptable'
    self.has_row(t, { 'badge': 'The Key' })
    self.yesno_column(yesno, t, 'firstName')
    disco = self.get_disco()
    self.response = self.client.get(reverse('show_item_detail', args=[int(disco.id)]))
    self.status_okay()
    self.yesno_column(yesno, 'item_people_table', 'person')

  def can_edit_programme(self, yesno):
    "Edit programme means: add/change/delete items, people"
    self.assertEqual(yesno, self.rootuser.has_perm('streampunk.edit_programme'))

    # Main page: menu items for adding people and items

    self.response = self.client.get(reverse('main_page'))
    self.status_okay()
    self.yesno_link_to(yesno, 'new_person')
    self.yesno_link_to(yesno, 'new_item')

    # People list: links to delete or edit.
    self.response = self.client.get(reverse('list_people'))
    self.status_okay()
    t = 'ptable'
    self.yesno_column(yesno, t, 'edit')
    self.yesno_column(yesno, t, 'remove')

    # show person - link to edit, add to an item, remove from an item or edit the item-person.
    # We don't test edit tags here - that's a separate permission.
    giles = self.get_giles()
    self.response  = self.client.get(reverse('show_person_detail', args=[int(giles.id)]))
    self.status_okay()
    t = 'person_items_table'
    self.yesno_link_to(yesno, 'edit_person', args=[int(giles.id)])
    self.yesno_column(yesno, t, 'edit')
    self.yesno_column(yesno, t, 'remove')
    self.yesno_link_to(yesno, 'new_itemperson')

    # Show item: edit item, add person to item, edit/remove the itemperson
    # We don't test edit tags here - that's a separate permission.
    # There should be full add/edit/remove for kit requests, but we ignore
    # other kit operations, as they fall under edit_kit.
    opening = self.get_openingceremony()
    self.response  = self.client.get(reverse('show_item_detail', args=[int(opening.id)]))
    self.status_okay()
    t = 'item_people_table'
    self.yesno_link_to(yesno, 'edit_item', args=[int(opening.id)])
    self.yesno_column(yesno, t, 'edit')
    self.yesno_column(yesno, t, 'remove')
    self.yesno_link_to(yesno, 'new_itemperson')

    t = 'krtable'
    self.yesno_link_to(yesno, 'add_kitrequest_to_item', args=[int(opening.id)])
    self.yesno_column(yesno, t, 'edit')
    self.yesno_column(yesno, t, 'remove')

    # A grid page should show the fill-slot links in each cell.
    # We're going to assume it's the unsched version that's wanted.
    for grid in opening.start.grid_set.all():
      self.response = self.client.get(reverse('show_grid', args=[int(grid.id)]))
      self.status_okay()
      self.yesno_link_to(yesno, 'fill_slot_unsched', args=[ int(opening.room.id), int(opening.start.id) ])

  def can_edit_kit(self, yesno):
    "Edit kit means: create/edit/del kit things and bundles, assign to/del from items and rooms."
    self.assertEqual(yesno, self.rootuser.has_perm('streampunk.edit_kit'))

    # Main page links for adding kit things, bundles. Also for adding to item or room.
    self.response = self.client.get(reverse('main_page'))
    self.status_okay()
    self.yesno_link_to(yesno, 'new_kitthing')
    self.yesno_link_to(yesno, 'new_kitbundle')
    self.yesno_link_to(yesno, 'add_kitthing_to_room')
    self.yesno_link_to(yesno, 'add_kitthing_to_item')
    self.yesno_link_to(yesno, 'add_kitbundle_to_room')
    self.yesno_link_to(yesno, 'add_kitbundle_to_item')

    # Show item has add kit thing to item, add kit bundle to item, edit or delete any existing assignments.
    qs = KitItemAssignment.objects.all()
    self.assertTrue(qs.count() > 0)
    kia = qs[0]
    self.response =  self.client.get(reverse('show_item_detail', args=[int(kia.item.id)]))
    self.status_okay()
    self.yesno_link_to(yesno, 'add_kitthing_to_item')
    self.yesno_link_to(yesno, 'add_kitbundle_to_item')
    t = 'kiatable'
    # KitItemTable has a remove column, but not an edit column.
    self.yesno_column(yesno, t, 'remove')
    
    # Show room has add kit thing to item, add kit bundle to room, edit or delete any existing assignments.
    # (XXX does/should edit room limit access to the kit-related attributes?)
    room = self.get_mainhall()
    self.response =  self.client.get(reverse('show_room_detail', args=[int(room.id)]))
    self.status_okay()
    self.yesno_link_to(yesno, 'add_kitthing_to_room')
    self.yesno_link_to(yesno, 'add_kitbundle_to_room')
    t = 'kratable'
    # KitRoomTable has a remove column, but not an edit column.
    self.yesno_column(yesno, t, 'remove')
    
    # list kit things/bundles shows edit/remove links, iff not in use.
    self.response = self.client.get(reverse('list_kitthings'))
    self.status_okay()
    t = 'kttable'
    self.yesno_column(yesno, t, 'edit')
    self.response = self.client.get(reverse('list_kitbundles'))
    self.status_okay()
    t = 'kbtable'
    # No Edit column in the KitBundleTable.
    self.yesno_column(yesno, t, 'remove')


    # show kit thing/bundle shows edit, and add to item/room.
    greenroomscr = self.get_greenroomscr()
    self.response = self.client.get(reverse('show_kitthing_detail', args=[int(greenroomscr.id)]))
    self.status_okay()
    self.yesno_link_to(yesno, 'edit_kitthing', args=[int(greenroomscr.id)])
    self.yesno_link_to(yesno, 'add_kitthing_to_item')
    self.yesno_link_to(yesno, 'add_kitthing_to_room')
    greenroomkit = self.get_greenroomkit()
    self.response = self.client.get(reverse('show_kitbundle_detail', args=[int(greenroomkit.id)]))
    self.status_okay()
    self.yesno_link_to(yesno, 'add_kitbundle_to_item')
    self.yesno_link_to(yesno, 'add_kitbundle_to_room')
    # The bundle's in use at this point, so we disallow the general editing of
    # bundles, even if we have edit_kit.
    if yesno:
      self.assertTrue('This bundle is in use' in self.response.content)
    else:
      self.yesno_link_to(yesno, 'edit_kitbundle', args=[int(greenroomkit.id)])
    # Now zap the use of the bundle - it should become editable, but only if we
    # have that permission.
    KitItemAssignment.objects.filter(bundle=greenroomkit).delete()
    KitRoomAssignment.objects.filter(bundle=greenroomkit).delete()
    self.response = self.client.get(reverse('show_kitbundle_detail', args=[int(greenroomkit.id)]))
    self.status_okay()
    self.assertFalse('This bundle is in use' in self.response.content)
    self.yesno_link_to(yesno, 'edit_kitbundle', args=[int(greenroomkit.id)])


  def can_config_db(self, yesno):
    "Config DB is the ability to add rooms, grids, slots, etc."
    self.assertEqual(yesno, self.rootuser.has_perm('streampunk.config_db'))

    # We consider adding a new room to be something special.
    self.response = self.client.get(reverse('main_page'))
    self.status_okay()
    self.yesno_link_to(yesno, 'new_room')

    # And all the other DB config stuff is done through the Admin interface,
    # So access to that interface should be controlled.
    self.yesno_link_to(yesno, 'admin:index')

  def can_edit_tags(self, yesno):
    "Edit tags: allows ability to create/delete/add/remove tags for items, people."
    self.assertEqual(yesno, self.rootuser.has_perm('streampunk.edit_tags'))

    # The banner has adding a new tag, and adding tags to stuff
    self.response = self.client.get(reverse('main_page'))
    self.status_okay()
    self.yesno_link_to(yesno, 'new_tag')
    self.yesno_link_to(yesno, 'add_tags')

    # The tag list has edit/remove options
    self.response = self.client.get(reverse('list_tags'))
    self.status_okay()
    t = 'ttable'
    self.yesno_column(yesno, t, 'edit')
    self.yesno_column(yesno, t, 'remove')

    # The show tag page has an edit option, and a list of uses, with remove options.
    comics = self.get_comics()
    self.response = self.client.get(reverse('show_tag_detail', args=[int(comics.id)]))
    self.status_okay()
    self.yesno_link_to(yesno, 'edit_tag', args=[int(comics.id)])
    # The table should never show edit/remove links, though - they change
    # the person, not the tag association.
    self.no_column('pttable', 'edit')
    self.no_column('pttable', 'remove')

    books = self.get_books()
    self.response = self.client.get(reverse('show_tag_detail', args=[int(books.id)]))
    self.status_okay()
    self.yesno_link_to(yesno, 'edit_tag', args=[int(books.id)])
    # Again, no edit/remove column should appear here, regardless of perms.
    self.no_column('ittable', 'edit')
    self.no_column('ittable', 'remove')

    # show person/item has a list of tags, with NO edit/remove options, and an edit tags for person/item option.
    giles = self.get_giles()
    self.response = self.client.get(reverse('show_person_detail', args=[int(giles.id)]))
    self.status_okay()
    self.yesno_link_to(yesno, 'edit_tags_for_person', args=[int(giles.id)])
    bidsession = self.get_bidsession()
    self.response = self.client.get(reverse('show_item_detail', args=[int(bidsession.id)]))
    self.status_okay()
    self.yesno_link_to(yesno, 'edit_tags_for_item', args=[int(bidsession.id)])

class test_concom(PermTest):
  "Check whether the concom users can do the right things."

  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.client = Client()
    self.logged_in_okay = self.client.login(username='fury', password='yyy')
    self.rootuser = User.objects.get(username='fury')

  def tearDown(self):
    self.client.logout()

  def test_yesno(self):
    "Check whether the yesno tests give the right results"
    self.can_read_private(True)
    self.can_edit_programme(True)
    self.can_config_db(False)
    self.can_edit_tags(True)
    self.can_edit_kit(True)


class test_constaff(PermTest):
  "Check whether the constaff users can do the right things."

  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.client = Client()
    self.logged_in_okay = self.client.login(username='phil', password='yyy')
    self.rootuser = User.objects.get(username='phil')

  def tearDown(self):
    self.client.logout()

  def test_yesno(self):
    "Check whether the yesno tests give the right results"
    self.can_read_private(True)
    self.can_edit_programme(False)
    self.can_config_db(False)
    self.can_edit_tags(False)
    self.can_edit_kit(False)


class test_participant(PermTest):
  "Check whether the participant users can do the right things."

  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.client = Client()
    self.logged_in_okay = self.client.login(username='mel', password='yyy')
    self.rootuser = User.objects.get(username='mel')

  def tearDown(self):
    self.client.logout()

  def test_yesno(self):
    "Check whether the yesno tests give the right results"
    self.can_read_private(False)
    self.can_edit_programme(False)
    self.can_config_db(False)
    self.can_edit_tags(False)
    self.can_edit_kit(False)


class test_progops(PermTest):
  "Check whether the progops users can do the right things."

  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.client = Client()
    self.logged_in_okay = self.client.login(username='grant', password='yyy')
    self.rootuser = User.objects.get(username='grant')

  def tearDown(self):
    self.client.logout()

  def test_yesno(self):
    "Check whether the yesno tests give the right results"
    self.can_read_private(True)
    self.can_edit_programme(True)
    self.can_config_db(False)
    self.can_edit_tags(True)
    self.can_edit_kit(False)


class test_streampunkadmin(PermTest):
  "Check whether the streampunkadmin users can do the right things."

  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.client = Client()
    self.logged_in_okay = self.client.login(username='fitz', password='yyy')
    self.rootuser = User.objects.get(username='fitz')

  def tearDown(self):
    self.client.logout()

  def test_yesno(self):
    "Check whether the yesno tests give the right results"
    self.can_read_private(True)
    self.can_edit_programme(True)
    self.can_config_db(True)
    self.can_edit_tags(True)
    self.can_edit_kit(True)


class test_tech(PermTest):
  "Check whether the tech users can do the right things."

  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.client = Client()
    self.logged_in_okay = self.client.login(username='sky', password='yyy')
    self.rootuser = User.objects.get(username='sky')

  def tearDown(self):
    self.client.logout()

  def test_yesno(self):
    "Check whether the yesno tests give the right results"
    self.can_read_private(True)
    self.can_edit_programme(False)
    self.can_config_db(False)
    self.can_edit_tags(True)
    self.can_edit_kit(True)

# ----------------------------------------------------------------------

class test_profiles(PermTest):
  "Check whether the user profiles work."

  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.client = Client()
    self.logged_in_okay = self.client.login(username='sky', password='yyy')
    self.rootuser = User.objects.get(username='sky')

  def tearDown(self):
    self.client.logout()

  def view_profile(self):
    "Can we see what's on our profile?"

    self.response = self.client.get(reverse('userprofile'))
    self.status_okay()
    self.has_link_to('editprofile')
    self.has_link_to('password_change')

  def edit_profile(self):
    "Can we change the user profile?"
    profile = self.rootuser.profile

    # show_shortname defaults to True. Make sure it is.
    self.assertTrue(profile.show_shortname)

    # Make sure we can fetch the form.
    self.response = self.client.get(reverse('editprofile'))
    self.status_okay()
    self.form_okay()

    # Post back, changing the show_shortname setting to False.
    self.response = self.client.post(reverse('editprofile'), {
      "show_shortname": False,
      "show_tags": True,
      "show_people": True,
      "show_kitthings": True,
      "show_kitbundles": True,
      "show_kitrequests": True,
      "rooms_across_top": True,
      "name_order": "Last"
    }, follow=True)
    self.status_okay()
    self.form_okay()
    # Refetch the profile, and make sure it has changed.
    profile = UserProfile.objects.get(id=profile.id)
    self.assertFalse(profile.show_shortname)
  
# ----------------------------------------------------------------------

class EmailTest(AuthTest):
  "Class to help out with testing the email functionality."

  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')
    # Make sure that each of the people have an email address
    peeps = { 'buffy@sunnydale.edu': { 
                 "method": self.get_buffy,
                 "contact": "Surburbs, Sunnydale",
               },
              'giles@britishmuseum.gov.uk': { 
                 "method": self.get_giles,
                 "contact": "British Museum, London",
               },
              'xander@basement.com': { 
                 "method": self.get_xander,
                 "contact": "Mom's basement, Sunnydale",
               },
              'willow@witchy.net': { 
                 "method": self.get_willow,
                 "contact": "With Amber",
               },
             }
    for addr in peeps.keys():
      peep = peeps[addr]
      meth = peep["method"]
      p = meth()
      p.email = addr
      p.contact = peep["contact"]
      p.save()

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def clear_outbox(self):
    mail.outbox = []

  def find_email(self, to, subj):
    "Look for the indicated message in the outbox."
    for msg in mail.outbox:
      if (subj == msg.subject) and (to in msg.to):
        return msg
    return None

  def email_match(self, msg, body):
    "Confirm that the body text appears in the body of the message."
    self.assertTrue(escape(body) in msg.body)

  def no_email_match(self, msg, body):
    "Confirm that the body text does not appear in the body of the message."
    self.assertFalse(escape(body) in msg.body)

  def yesno_items_included(self, yesno, msg, person):
    "Confirm that the item titles appear in the message, iff yesno is True."
    for ip in ItemPerson.objects.filter(person=person):
      self.yesno_email_match(yesno, msg, ip.item.title)

  def items_included(self, msg, person):
    return self.yesno_items_included(True, msg, person)

  def no_items_included(self, msg, person):
    return self.yesno_items_included(False, msg, person)

  def yesno_avail_included(self, yesno, msg, person):
    "Check that availability is included in the msg iff yesno is True."
    # Need to be careful what we check - a slot's text can appear in
    # a message because we've included the availability or because we've
    # included items, and it's the start time. So separate out the two
    # categories, because we don't know, here, whether items are included.

    avail_slots = set(list(person.availability.all()))
    start_slots = set([ i.start for i in person.item_set.all() ])
    every_slot = set(list(Slot.objects.all()))
    overlap_slots = avail_slots & start_slots
    both_slots = avail_slots | start_slots
    avail_only_slots = avail_slots - start_slots
    neither_slots = every_slot - both_slots

    self.assertTrue(len(avail_only_slots) > 0)
    self.assertTrue(len(neither_slots) > 0)
    self.assertTrue(len(overlap_slots) > 0)
    # if yesno:
    #   All the slots in avail_only_slots should be there, because
    #   avails are included.
    # else:
    #   None of the slots in avail_only_slots should be there, because
    #   avails are not included.
    for slot in avail_only_slots:
      self.yesno_email_match(yesno, msg, str(slot))

    # Slots that are neither avail nor item starts definitely
    # should not be there, regardless of whether we've included
    # items or availability.
    for slot in neither_slots:
      self.no_email_match(msg, str(slot))

    # Slots in the overlap might be there for item inclusion, but
    # definitely should be there if we've included the availability.
    if yesno:
      for slot in overlap_slots:
        self.email_match(msg, str(slot))

  def avail_included(self, msg, person):
    self.yesno_avail_included(True, msg, person)

  def no_avail_included(self, msg, person):
    self.yesno_avail_included(False, msg, person)

  def yesno_email_match(self, yesno, msg, body):
    "Confirm that the body text appears in the msg, iff yesno is true."
    if yesno:
      self.assertTrue(escape(body) in msg.body)
    else:
      self.assertFalse(escape(body) in msg.body)

  def subj(self):
    "A default subject"
    return "On the Fallability of Humanity"

  def body(self):
    "A default body"
    return """
           This is the default body of text.
           It's not very exciting. But such is life.

           We have linebreaks, too. And cookies.

           Yours,

           Colonel Witherington-Smythe (retired)
           """

class test_email_person(EmailTest):
  "Check the permutations of email_person() view."

  def test_get_form(self):
    "Check it's okay to get a form for a person."
    giles = self.get_giles()
    self.assertTrue(giles.email)
    self.response = self.client.get(reverse('email_person', args=[int(giles.id)]))
    self.status_okay()
    self.form_okay()

  def test_post_message_and_subject(self):
    "Check we can email a normal message, without extras."
    giles = self.get_giles()
    self.response = self.client.post(reverse('email_person', args=[int(giles.id)]), {
      "subject": self.subj(),
      "message": self.body(),
    }, follow=True)
    self.status_okay()
    self.form_okay()
    self.assertTemplateUsed(response=self.response, template_name='streampunk/emailed.html')
    msg = self.find_email(giles.email, self.subj())
    self.email_match(msg, self.body())
    self.no_items_included(msg, giles)
    self.no_avail_included(msg, giles)
    self.no_email_match(msg, giles.contact)

  def test_post_message_and_subject_and_items(self):
    "Check we can email a normal message, with item listings."
    giles = self.get_giles()
    self.response = self.client.post(reverse('email_person', args=[int(giles.id)]), {
      "subject": self.subj(),
      "message": self.body(),
      "includeItems": True,
    }, follow=True)
    self.status_okay()
    self.form_okay()
    self.assertTemplateUsed(response=self.response, template_name='streampunk/emailed.html')
    msg = self.find_email(giles.email, self.subj())
    self.email_match(msg, self.body())
    self.items_included(msg, giles)
    self.no_avail_included(msg, giles)
    self.no_email_match(msg, giles.contact)

  def test_post_message_and_subject_and_avail(self):
    "Check we can email a normal message, with availability."
    giles = self.get_giles()
    self.response = self.client.post(reverse('email_person', args=[int(giles.id)]), {
      "subject": self.subj(),
      "message": self.body(),
      "includeAvail": True,
    }, follow=True)
    self.status_okay()
    self.form_okay()
    self.assertTemplateUsed(response=self.response, template_name='streampunk/emailed.html')
    msg = self.find_email(giles.email, self.subj())
    self.email_match(msg, self.body())
    slots = giles.availability.all()
    self.avail_included(msg, giles)
    self.no_items_included(msg, giles)
    self.no_email_match(msg, giles.contact)

  def test_post_message_and_subject_and_contact(self):
    "Check we can email a normal message, with contact details."
    giles = self.get_giles()
    self.response = self.client.post(reverse('email_person', args=[int(giles.id)]), {
      "subject": self.subj(),
      "message": self.body(),
      "includeContact": True,
    }, follow=True)
    self.status_okay()
    self.form_okay()
    self.assertTemplateUsed(response=self.response, template_name='streampunk/emailed.html')
    msg = self.find_email(giles.email, self.subj())
    self.email_match(msg, self.body())
    self.no_avail_included(msg, giles)
    self.no_items_included(msg, giles)
    self.email_match(msg, giles.contact)

  def test_post_message_with_everything(self):
    "Check we can email a normal message, with all the extras."
    giles = self.get_giles()
    self.response = self.client.post(reverse('email_person', args=[int(giles.id)]), {
      "subject": self.subj(),
      "message": self.body(),
      "includeContact": True,
      "includeAvail": True,
      "includeItems": True,
    }, follow=True)
    self.status_okay()
    self.form_okay()
    self.assertTemplateUsed(response=self.response, template_name='streampunk/emailed.html')
    msg = self.find_email(giles.email, self.subj())
    self.email_match(msg, self.body())
    self.avail_included(msg, giles)
    self.items_included(msg, giles)
    self.email_match(msg, giles.contact)

class test_personlist(AuthTest):
  "Check list creation, display and deletion."
  fixtures = [ 'demo_data' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_creation(self):
    "Check we can create a personlist."
    # Creating a personlist has the following steps:
    # 1. A page displays a PersonTable, with a form to create some/all of the list.
    # 2. The form is posted, which displays the make_personlist page. That asks for
    #    a name, and whether to automatically delete as well. It also allows you to
    #    change the people in the list.
    # 3. That form is submitted. We go to http://localhost/streampunk/peoplelists/
    self.assertEqual(PersonList.objects.count(), 2)
    self.assertTrue(PersonList.objects.filter(name='Scoobie Gang').exists())
    self.assertTrue(PersonList.objects.filter(name='Serenity Crew').exists())
    allpeeps = [ int(p.id) for p in Person.objects.all() ]

    # Post to make_person
    self.response = self.client.post(reverse('make_personlist'), {
      "save_all": True,
      "allpeople": allpeeps,
    }, follow=True)
    self.status_okay()
    self.form_okay()
    # Get back the edit form
    self.assertTemplateUsed(response=self.response, template_name='streampunk/edit_personlist.html')

    # Post to the edit form. We use new_personlist here, because it hasn't been
    # created yet.
    self.response = self.client.post(reverse('new_personlist'), {
      "name": "Everybody",
      "auto": False,
      "people": allpeeps,
    }, follow=True)
    self.status_okay()
    self.form_okay()

    # Get back the list of lists
    self.assertTemplateUsed(response=self.response, template_name='streampunk/object_list.html')
    self.assertEqual(PersonList.objects.count(), 3)
    self.assertTrue(PersonList.objects.filter(name='Everybody').exists())

  def test_deletion(self):
    "Check that we can delete a personlist."
    self.assertEqual(PersonList.objects.count(), 2)
    self.assertTrue(PersonList.objects.filter(name='Scoobie Gang').exists())
    self.assertTrue(PersonList.objects.filter(name='Serenity Crew').exists())
    scoobies = PersonList.objects.get(name='Scoobie Gang')

    self.response = self.client.post(reverse('delete_personlist', args=[int(scoobies.id)]), follow=True)
    self.status_okay()
    self.assertEqual(PersonList.objects.count(), 1)
    self.assertFalse(PersonList.objects.filter(name='Scoobie Gang').exists())
    self.assertTrue(PersonList.objects.filter(name='Serenity Crew').exists())

  def test_editing(self):
    "Check we can edit the members of a personlist."

    # Fetch the Scoobie Gang, and take a look at its contents.
    buffy = self.get_buffy()
    dawn = self.get_dawn()
    scoobies = PersonList.objects.get(name='Scoobie Gang')
    self.assertTrue(buffy in scoobies.people.all())
    self.assertTrue(dawn in scoobies.people.all())
    self.assertEqual(scoobies.people.count(), 5)

    # Display the personlist, and check that too.

    self.response = self.client.get(reverse('show_personlist_detail', args=[int(scoobies.id)]))
    self.status_okay()
    self.assertTrue(buffy.badge in self.response.content)
    self.assertTrue(dawn.badge in self.response.content)

    # Get an editing form

    self.response = self.client.get(reverse('edit_personlist', args=[int(scoobies.id)]))
    self.status_okay()
    self.form_okay()
  
    # Submit an edited form. We want the list to contain everyone other than Buffy.
    others = scoobies.people.exclude(id=buffy.id)
    self.assertEqual(others.count(), 4)

    self.response = self.client.post(reverse('edit_personlist', args=[int(scoobies.id)]), {
      "name": scoobies.name,
      "auto": scoobies.auto,
      "created": scoobies.created,
      "people": [ int(p.id) for p in others ]
    }, follow=True)
    self.status_okay()
    self.form_okay()

    # Refetch the list. Check that it's changed.
    scoobies = PersonList.objects.get(name='Scoobie Gang')
    self.assertEqual(scoobies.people.count(), 4)
    self.assertFalse(buffy in scoobies.people.all())
    self.assertTrue(dawn in scoobies.people.all())

class test_email_personlist(EmailTest):
  "Check we can send email to personlists."

  fixtures = [ 'demo_data' ]

  def test_email_existing_list(self):
    "Check we can send email to a list that already exists"

    buffy = self.get_buffy()
    giles = self.get_giles()
    xander = self.get_xander()
    willow = self.get_willow()
    dawn = self.get_dawn()
    scoobies = PersonList.objects.get(name='Scoobie Gang')

    scoobie_peeps = scoobies.people.all()
    for p in [ buffy, giles, xander, willow, dawn ]:
      self.assertTrue(p in scoobie_peeps)

    # Get a form for sending to the list
    self.response = self.client.get(reverse('email_personlist', args=[int(scoobies.id)]))
    self.status_okay()
    self.form_okay()
    self.assertFalse('Something broke' in self.response.content)

    # Send a email message that goes to each person in the list that
    # has an email address - that should be everyone other than Dawn.
    # Do this by submitting a form.
    self.response = self.client.post(reverse('email_personlist', args=[int(scoobies.id)]), {
      "subject": self.subj(),
      "message": self.body(),
      "includeItems": False,
      "includeContact": False,
      "includeAvail": False
    }, follow=True)
    self.status_okay()
    self.form_okay()

    # Confirm that the personlist still exists
    self.assertTrue(PersonList.objects.filter(name='Scoobie Gang').exists())

    # Check that we've sent the correct number of messages
    self.assertEqual(len(mail.outbox), 4)
    for p in [ buffy, giles, xander, willow ]:
      msg = self.find_email(p.email, self.subj())
      self.assertTrue(msg)
      self.email_match(msg, self.body())
      self.no_items_included(msg, p)
      self.no_email_match(msg, p.contact)

    # Clear the outbox
    mail.outbox = []

    # Mail again, but this time include the items and contact
    self.response = self.client.post(reverse('email_personlist', args=[int(scoobies.id)]), {
      "subject": self.subj(),
      "message": self.body(),
      "includeItems": True,
      "includeContact": True,
      "includeAvail": False
    }, follow=True)
    self.status_okay()
    self.form_okay()

    # Check that we've sent the correct number of messages
    self.assertEqual(len(mail.outbox), 4)
    for p in [ buffy, giles, xander, willow ]:
      msg = self.find_email(p.email, self.subj())
      self.assertTrue(msg)
      self.email_match(msg, self.body())
      self.items_included(msg, p)
      self.email_match(msg, p.contact)


  def test_delete_after_sending(self):
    "Check the list gets deleted after sending if auto."

    buffy = self.get_buffy()
    giles = self.get_giles()
    xander = self.get_xander()
    willow = self.get_willow()
    scoobies = PersonList.objects.get(name='Scoobie Gang')

    # Mark it for auto-deletion
    scoobies.auto = True
    scoobies.save()

    scoobie_peeps = scoobies.people.all()
    for p in [ buffy, giles, xander, willow ]:
      self.assertTrue(p in scoobie_peeps)

    # Send a email message that goes to each person in the list that
    # has an email address - that should be everyone other than Dawn.
    # Do this by submitting a form.
    self.response = self.client.post(reverse('email_personlist', args=[int(scoobies.id)]), {
      "subject": self.subj(),
      "message": self.body(),
      "includeItems": False,
      "includeContact": False,
      "includeAvail": False
    }, follow=True)
    self.status_okay()
    self.form_okay()

    # Confirm that the personlist no longer exists
    self.assertFalse(PersonList.objects.filter(name='Scoobie Gang').exists())

    # Check that we've sent the correct number of messages
    self.assertEqual(len(mail.outbox), 4)
    for p in [ buffy, giles, xander, willow ]:
      msg = self.find_email(p.email, self.subj())
      self.assertTrue(msg)

class test_email_item(EmailTest):
  "check that we can email the people on an item."

  # When we show an item, we have personlist creation options
  # which also have an item ID attached, which changes the form
  # presented when the personlist creation is submitted.

  def test_make_personlist_with_iid(self):
    "Submit a personlist, with an item id."

    listname = 'Mail Disco Peeps'
    disco = self.get_disco()
    buffy = self.get_buffy()
    peeps = disco.people.all()
    self.response = self.client.post(reverse('make_personlist'), {
      "email_select": True,
      "listname": listname,
      "itemid": int(disco.id),
      "select": [ int(p.id) for p in peeps ]
    }, follow=True)
    self.status_okay()
    self.form_okay()
    # When submitted, the presence of the iid should have caused a redirect to
    # mail_item_with_personlist, so we'll get back the form to fill in.
    self.assertTemplateUsed(response=self.response, template_name='streampunk/mail_personlist.html')

    # There should now be a personlist for the item.
    plist = PersonList.objects.get(name=listname)
    # And it should have auto set, so that it's deleted regardless of the success/cancel button used.
    self.assertTrue(plist.auto)
    
    # so now we can send email to the people on that item using that personlist.
    # invoke mail_item_with_personlist again, directly this time, so we know that happened.
    mail_item_url = reverse('mail_item_with_personlist', args=[int(disco.id), int(plist.id)])
    self.response = self.client.get(mail_item_url)
    self.status_okay()
    self.form_okay()
    self.assertTemplateUsed(response=self.response, template_name='streampunk/mail_personlist.html')

    # Invoke again, posting this time, but via the cancel button. It should take us back to the item,
    # and it should delete the list..
    self.response = self.client.post(mail_item_url, { "cancel": True }, follow=True)
    self.status_okay()
    self.form_okay()
    self.assertTemplateUsed(response=self.response, template_name='streampunk/show_item.html')
    self.assertEqual(PersonList.objects.filter(name=listname).count(), 0)
    # No email should have been sent
    self.assertEqual(len(mail.outbox), 0)

    # Create the list again...
    self.response = self.client.post(reverse('make_personlist'), {
      "email_select": True,
      "listname": listname,
      "itemid": int(disco.id),
      "select": [ int(p.id) for p in peeps ]
    }, follow=True)
    self.status_okay()
    self.form_okay()

    # that'll create the list anew, with a new id.
    plist = PersonList.objects.get(name=listname)
    mail_item_url = reverse('mail_item_with_personlist', args=[int(disco.id), int(plist.id)])

    # now post to it again, but this time via the submit button. The list should still be deleted,
    # but email should get sent.

    self.response = self.client.post(mail_item_url, {
      "subject": self.subj(),
      "message": self.body()
    }, follow=True)
    self.status_okay()
    self.form_okay()
    self.assertTemplateUsed(response=self.response, template_name='streampunk/emailed.html')
    # Of the people in the list, only Buffy has an email address
    self.assertEqual(len(mail.outbox), 1)
    msg = self.find_email(buffy.email, self.subj())
    self.email_match(msg, self.body())

    # and the list should be gone again
    self.assertEqual(PersonList.objects.filter(name=listname).count(), 0)

class test_styles(StreampunkTest):
  "Check the stylesheet retrieval."

  def test_xsl(self):
    "Pull down the XSL page."
    self.response = self.client.get(reverse('xml_xsl'))
    self.status_okay()

class test_static_pages(StreampunkTest):
  "Check we retrieve static pages correctly."

  def test_about_etc(self):
    "Check About, Legal."

    self.response = self.client.get(reverse('about'))
    self.status_okay()
    self.assertTemplateUsed(response=self.response, template_name='streampunk/about.html')
    self.response = self.client.get(reverse('legal'))
    self.status_okay()
    self.assertTemplateUsed(response=self.response, template_name='streampunk/legal.html')

  def test_help(self):
    "Check Help pages."

    self.response = self.client.get(reverse('help_intro'))
    self.status_okay()
    self.assertTemplateUsed(response=self.response, template_name='help/help.html')
    self.response = self.client.get(reverse('help_grids'))
    self.status_okay()
    self.assertTemplateUsed(response=self.response, template_name='help/grids.html')


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
# 404 templates
