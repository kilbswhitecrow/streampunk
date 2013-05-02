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
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from streampunk.models import Grid, Gender, Slot, SlotLength, Room
from streampunk.models import ItemKind, SeatingKind, FrontLayoutKind
from streampunk.models import Revision, MediaStatus, ItemPerson, Tag
from streampunk.models import PersonStatus, PersonRole, Person, Item

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
    # items() will be the rendered cell content, inclding links.
    # Note also that the keys in the record dict need not match the titles
    # of the columns
    t = self.response.context[table]
    for row in t.rows:
      if rec <= row.record:
        # all of rec' keys appear in the row's record. Now get a list of
        # all the keys where the values are different. If this list is
        # empty, then this row matches the rec.
        diffs = [ k for k in rec.keys() if not k in row.record or rec[k] != row.record[k] ]
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

    def default_person(extras):
      p = {
        "firstName":      "Rupert",
        "lastName":       "Giles",
        "badge":          "Ripper",
        "memnum":         -1,
        "gender":         Gender.objects.find_default().id,
        "complete":       "No",
        "distEmail":      "No",
        "recordingOkay":  "No"
      }
      for k in extras.keys():
        p[k] = extras[k]
      return p

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
    def default_item(extras):
      i = {
        "title":       "Some Item",
        "shortname":   "some item",
        "start":       Slot.objects.find_default().id,
        "length":      SlotLength.objects.find_default().id,
        "room":        Room.objects.find_default().id,
        "kind":        ItemKind.objects.find_default().id,
        "seating":     SeatingKind.objects.find_default().id,
        "frontLayout": FrontLayoutKind.objects.find_default().id,
        "revision":    Revision.objects.latest().id,
        "expAudience": 0,
        "gophers":     0,
        "stewards":    0,
        "budget":      0,
        "projNeeded":  "No",
        "techNeeded":  "No",
        "complete":    "No",
        "visible":     True,
        "mediaStatus":  MediaStatus.objects.find_default().id
      }
      for k in extras.keys():
        i[k] = extras[k]
      return i

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
  fixtures = [ 'room', 'person', 'items', 'tags', 'avail', 'kit' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_people_items(self):
    def default_itemperson(extras):
      ip = {
        "item": None,
        "person": None,
        "role": PersonRole.objects.find_default().id,
        "status": PersonStatus.objects.find_default().id,
        "visible": True,
        "distEmail": "No",
        "recordingOkay": "No"
      }
      for k in extras.keys():
        ip[k] = extras[k]
      return ip
  
    buffy = Person.objects.get(firstName='Buffy')
    giles = Person.objects.get(lastName='Giles')
    ceilidh = Item.objects.get(shortname='Ceilidh')
    disco = Item.objects.get(shortname='Disco')
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
    def pdict(person):
      return {
        "firstName":      person.firstName,
        "lastName":       person.lastName,
        "badge":          person.badge,
        "memnum":         person.memnum,
        "gender":         person.gender.id,
        "complete":       person.complete,
        "distEmail":      person.distEmail,
        "recordingOkay":  person.recordingOkay
      }

    buffy = Person.objects.get(firstName='Buffy')
    eaddr = 'buffy@sunnydale.net'
    self.response = self.client.get(reverse('edit_person', kwargs={ "pk": buffy.id }))
    self.status_okay()
    object = self.response.context['object']
    postdata = pdict(object)
    postdata['email'] = eaddr
    self.response = self.client.post(reverse('edit_person', kwargs={ "pk": buffy.id }), postdata, follow=True)
    self.status_okay()
    person = self.response.context['person']
    self.assertEqual(buffy.id, person.id)
    self.assertEqual(eaddr, person.email)
    buf2 = Person.objects.get(email=eaddr)
    self.assertEqual(buffy.id, buf2.id)

  def test_person_tags(self):
    def chk_tags(person, taglist):
      # Check the person has the right tags.
      alltags = person.tags.all()
      self.assertEqual(alltags.count(), len(taglist))
      for tag in taglist:
        self.assertTrue(tag in alltags)
      # Check the page shows the right tags.
      t = 'tagtable'
      self.response = self.client.get(reverse('show_person_detail', kwargs={'pk': person.id}))
      self.status_okay()
      self.assertEqual(self.num_rows(t), len(taglist))
      for tag in taglist:
        self.has_row(t, { "name": tag.name })

    def tagids(tagqs):
      return [ t.id for t in tagqs ]

    buffy = Person.objects.get(firstName='Buffy')
    giles = Person.objects.get(lastName='Giles')
    books = Tag.objects.get(name='Books')
    movies = Tag.objects.get(name='Movies')

    # No tags for anyone yet
    chk_tags(buffy, [])
    chk_tags(giles, [])
    self.response = self.client.get(reverse('edit_tags_for_person', args=[ buffy.id ]))
    self.status_okay()

    fperson = self.response.context['person']

    # Create a new set of tags, that has a couple more
    newtags = [ t for t in fperson.tags.all() ] + [ books, movies ]
    self.response = self.client.post(reverse('edit_tags_for_person', args=[ buffy.id ]), {
      "tags": tagids(newtags)
    }, follow=True)
    self.status_okay()
    chk_tags(buffy, newtags)
    chk_tags(giles, [])

    # Again, but with only one new tag.
    # Looks like this particular test currently fails.
    newtags = [ books ]
    self.response = self.client.post(reverse('edit_tags_for_person', args=[ buffy.id ]), {
      "tags": tagids(newtags)
    }, follow=True)
    self.status_okay()
    chk_tags(buffy, newtags)
    chk_tags(giles, [])

    # If we include tags twice, they should not get added twice.
    newtags = [ books, movies ]
    toomanytags = newtags + [ books, movies ]
    self.response = self.client.post(reverse('edit_tags_for_person', args=[ buffy.id ]), {
      "tags": tagids(toomanytags)
    }, follow=True)
    self.status_okay()
    chk_tags(buffy, newtags)
    chk_tags(giles, [])

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
  fixtures = [ 'room', 'person', 'items', 'tags', 'avail', 'kit' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_people_items(self):
    def default_itemperson(extras):
      ip = {
        "item": None,
        "person": None,
        "role": PersonRole.objects.find_default().id,
        "status": PersonStatus.objects.find_default().id,
        "visible": True,
        "distEmail": "No",
        "recordingOkay": "No"
      }
      for k in extras.keys():
        ip[k] = extras[k]
      return ip
  
    buffy = Person.objects.get(firstName='Buffy')
    willow = Person.objects.get(firstName='Willow')
    dawn = Person.objects.get(firstName='Dawn')
    disco = Item.objects.get(shortname='Disco')
    ceilidh = Item.objects.get(shortname='Ceilidh')
    books = Tag.objects.get(name='Books')
    movies = Tag.objects.get(name='Movies')
    panellist = PersonRole.objects.get(name='Panellist')

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

class test_delete_items(AuthTest):
  "Deleting people"
  fixtures = [ 'room', 'person', 'items', 'tags', 'avail', 'kit' ]

  def setUp(self):
    self.mkroot()
    self.client = Client()
    self.logged_in_okay = self.client.login(username='congod', password='xxx')

  def tearDown(self):
    self.client.logout()
    self.zaproot()

  def test_people_items(self):
    def default_itemperson(extras):
      ip = {
        "item": None,
        "person": None,
        "role": PersonRole.objects.find_default().id,
        "status": PersonStatus.objects.find_default().id,
        "visible": True,
        "distEmail": "No",
        "recordingOkay": "No"
      }
      for k in extras.keys():
        ip[k] = extras[k]
      return ip
  
    buffy = Person.objects.get(firstName='Buffy')
    willow = Person.objects.get(firstName='Willow')
    dawn = Person.objects.get(firstName='Dawn')
    disco = Item.objects.get(shortname='Disco')
    ceilidh = Item.objects.get(shortname='Ceilidh')
    bid = Item.objects.get(shortname='bid session')
    books = Tag.objects.get(name='Books')
    movies = Tag.objects.get(name='Movies')
    panellist = PersonRole.objects.get(name='Panellist')

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


# Tests required
# 	Delete item
# 		with kit requests
# 		with kit things
# 		with kit bundles
# 	Delete tag
# 		solo
# 		when on people
# 		when on items
# 	Delete room
# 		solo
# 		With items in room
# 		With capacities
# 		with kit things
# 		with kit bundles
# 
# Items
#	Edit
#	Add tags
#	Remove tags
#	Lookup tags
#	Add too many tags
#	Change room
#	Look up in room
# 	Kit request
# 		Create and Add to item
# 		List
# 		Edit when solo
# 		Remove from item and delete
# 		Edit when on item
# 	Kit thing
# 		Create
# 		List
# 		Edit, when solo
# 		Add to item
# 		Add to room
# 		Edit, when on item
# 		Edit, when on room
# 		Delete, when on item
# 		Delete, when on room
# 		In kit usage
# 	Kit bundle
# 		List
# 		Create, empty
# 		Create, with contents
# 		Edit, when solo
# 		Delete, when solo
# 		Add to item
# 		edit, when on item
# 		add to room
# 		edit, when in room
# 		in kit usage
# 	Satisfaction
# 		not satisfied - no thing
# 		not satisfied - insufficient count
# 		not satisfied - wrong type
# 		not satisfied - thing satisfies other request on item
# 		not satisfied - thing on room finishes sooner
# 		not satisfied - thing on room starts later
# 		satisfied by thing on item
# 		satisfied by thing in room
# 		included in not-satisfied list
# 		satisfied-by listing is correct
# 
# 	Availability
# 		Create and add to person
# 		Create and add to room
# 		Create and add to thing
# 		Edit solo
# 		Edit when on prson
# 		Edit when on thing
# 		Edit when on room
# 		Delete solo
# 		Delete when on person
# 		Delete when on thing
# 		Delete when on room
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
# 		items iwth unsatisfied kit requests
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
