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

from django.core.urlresolvers import reverse

from .models import PersonRole, PersonStatus
from .models import Slot, SlotLength, Room, ItemKind, SeatingKind
from .models import FrontLayoutKind, Revision, MediaStatus
from .models import Gender, KitKind, KitRole, KitSource, KitDepartment
from .models import KitBasis, KitStatus, Check

def modeldict(i, conv):
  """
  Given an object, return a dict suitable for posting back. conv is a dict that indicates
  which attributes should be convert to ids ('objects') and which are just values ('values').
  """
  d = dict()

  # attributes that are just values
  for k in conv['values']:
    d[k] = getattr(i, k)

  # for attributes that are model objects, we want to post back the id.
  for k in conv['objects']:
    try:
      d[k] = getattr(i, k).id
    except AttributeError:
      pass
  return d

def itemdict(i):
  "Given an item object, return a dict suitable for posting back."
  d = dict()

  # attributes that are just values
  d['values'] = [ 'title', 'shortname', 'blurb', 'revision', 'expAudience',
                  'gophers', 'stewards', 'budget', 'projNeeded', 'techNeeded',
                  'complete', 'privNotes', 'techNotes', 'pubBring', 'audienceMics',
                  'allTechCrew', 'needsReset', 'needsCleanUp' ]

  # for attributes that are model objects, we want to post back the id.
  d['objects'] = [ 'start', 'length', 'room', 'kind', 'seating', 'frontLayout',
                   'revision', 'follows', 'mediaStatus' ]
  return modeldict(i, d)

def persondict(p):
  "Given a person object, return a dict suitable for posting back."

  d = dict()

  # attributes that are just values
  d['values'] = [ 'firstName', 'lastName', 'badge', 'memnum', 'complete', 'distEmail',
                  'recordingOkay' ]

  # for attributes that are model objects, we want to post back the id.
  d['objects'] = [ 'gender' ]
  return modeldict(p, d)

def kitreqdict(p):
  "Given a kit request object, return a dict suitable for posting back."

  d = dict()

  # attributes that are just values
  d['values'] = [ 'count', 'setupAssistance', 'notes' ]

  # for attributes that are model objects, we want to post back the id.
  d['objects'] = [ 'kind', 'status' ]
  return modeldict(p, d)

def kitthingdict(p):
  "Given a kit thing object, return a dict suitable for posting back."

  d = dict()

  # Attributes that are just values
  d['values'] = [ 'name', 'description', 'count', 'cost', 'insurance', 'notes', 'coordinator' ]

  # for attributes that are model objects, we want to post back the id.
  d['objects'] = [ 'kind', 'role', 'source', 'department', 'basis', 'status' ]
  return modeldict(p, d)


def kitbundledict(p):
  "Given a kit bundle object, return a dict suitable for posting back."
  d = dict()
  d['name' ] = p.name
  d['status'] = p.status.id
  d['things'] = [ thing.id for thing in p.things.all() ]
  return d

def def_extras(d, extras):
  for k in extras.keys():
    d[k] = extras[k]
  return d

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
  return def_extras(p, extras)

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
  return def_extras(i, extras)

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
  return def_extras(ip, extras)

def default_kitthing(extras):
  kt = {
    "name": "Bob's Thing",
    "description": "A blue box",
    "kind": KitKind.objects.find_default().id,
    "count": 1,
    "role": KitRole.objects.find_default().id,
    "source": KitSource.objects.find_default().id,
    "department": KitDepartment.objects.find_default().id,
    "basis": KitBasis.objects.find_default().id,
    "status": KitStatus.objects.find_default().id,
    "insurance": 0,
    "cost": 0,
    "coordinator": "Bob"
  }
  return def_extras(kt, extras)

def default_kitbundle(extras):
  kb = {
    "name": "Bob's Bundles",
    "status": KitStatus.objects.find_default().id,
    "things": [ ]
  }
  return def_extras(kb, extras)

def default_kitrequest(extras):
  kr = {
    "kind": KitKind.objects.find_default().id,
    "count": 1,
    "setupAssistance": False,
    "notes": "This is easy.",
    "status": KitStatus.objects.find_default().id
  }
  return def_extras(kr, extras)


def item_lists_req(self, item, req, yesno):
  "Check whether the kit request appears on the item's page."

  self.response = self.client.get(reverse('show_item_detail', args=[ item.id ]))
  if yesno:
    self.has_row('krtable', { "kind": req.kind, "count": req.count })
  else:
    self.no_row('krtable', { "kind": req.kind, "count": req.count })

def item_lists_thing(self, item, thing, yesno):
  "Check whether the kit thing appears on the item's page."

  self.response = self.client.get(reverse('show_item_detail', args=[ item.id ]))
  if yesno:
    self.has_row('kiatable', { "thing": thing.name })
  else:
    self.no_row('kiatable', { "thing": thing.name })

def item_lists_bundle(self, item, bundle, yesno):
  "Check whether the kit bundle appears on the item's page."

  self.response = self.client.get(reverse('show_item_detail', args=[ item.id ]))
  if yesno:
    self.has_row('kiatable', { "bundle": bundle.name })
  else:
    self.no_row('kiatable', { "bundle": bundle.name })

def req_lists_item(self, req, item, yesno):
  "Check whether the kit request lists use by the item."

  self.response = self.client.get(reverse('show_kitrequest_detail', args=[ req.id ]))
  if yesno:
    self.has_row('itable', { "item": item.title })
  else:
    self.no_row('itable', { "item": item.title })

def thing_lists_item(self, thing, item, yesno):
  "Check whether the kit thing lists use by the item."

  self.response = self.client.get(reverse('show_kitthing_detail', args=[ thing.id ]))
  if yesno:
    self.has_row('kiatable', { "item": item.title })
  else:
    self.no_row('kiatable', { "item": item.title })

def bundle_lists_item(self, bundle, item, yesno):
  "Check whether the kit bundle lists use by the item."

  self.response = self.client.get(reverse('show_kitbundle_detail', args=[ bundle.id ]))
  if yesno:
    self.has_row('kiatable', { "item": item.title })
  else:
    self.no_row('kiatable', { "item": item.title })

def usage_lists_req_for_item(self, req, item, yesno):
  "Check whether the kit-usage page lists the req being used by the item."
  self.response = self.client.get(reverse('kit_usage'))
  if yesno:
    self.has_row('krtable', { "kind": req.kind, "count": req.count })
  else:
    self.no_row('krtable', { "kind": req.kind, "count": req.count })

def usage_lists_thing_for_item(self, thing, item, yesno):
  "Check whether the kit-usage page lists the thing being used by the item."
  self.response = self.client.get(reverse('kit_usage'))
  if yesno:
    self.has_row('kiatable', { "thing": thing.name, "item": item.title, "room": item.room.name })
  else:
    self.no_row('kiatable', { "thing": thing.name, "item": item.title, "room": item.room.name })

def usage_lists_bundle_for_item(self, bundle, item, yesno):
  "Check whether the kit-usage page lists the bundle being used by the item."
  self.response = self.client.get(reverse('kit_usage'))
  if yesno:
    self.has_row('kiatable', { "bundle": bundle.name, "item": item.title, "room": item.room.name })
  else:
    self.no_row('kiatable', { "bundle": bundle.name, "item": item.title, "room": item.room.name })

def usage_lists_thing_for_room(self, thing, room, yesno):
  "Check whether the kit-usage page lists the thing being assigned to the room."
  self.response = self.client.get(reverse('kit_usage'))
  if yesno:
    self.has_row('kratable', { "thing": thing.name, "room": room.name })
  else:
    self.no_row('kratable', { "thing": thing.name, "room": room.name })

def usage_lists_bundle_for_room(self, bundle, room, yesno):
  "Check whether the kit-usage page lists the bundle being assigned to the room."
  self.response = self.client.get(reverse('kit_usage'))
  if yesno:
    self.has_row('kratable', { "bundle": bundle.name, "room": room.name })
  else:
    self.no_row('kratable', { "bundle": bundle.name, "room": room.name })

def bundle_lists_thing(self, bundle, thing, yesno):
  "Check whether the detail page for the bundle lists the thing."
  self.response = self.client.get(reverse('show_kitbundle_detail', args=[bundle.id]))
  if yesno:
    self.has_row('kttable', { "name": thing.name, "count": thing.count })
  else:
    self.no_row('kttable', { "name": thing.name, "count": thing.count })

def thing_lists_bundle(self, thing, bundle, yesno):
  "Check whether the thing thinks it's used by the bundle."
  self.response = self.client.get(reverse('show_kitthing_detail', args=[thing.id]))
  if yesno:
    self.has_row('kbtable', { 'name': bundle.name })
  else:
    self.no_row('kbtable', { 'name': bundle.name })

def item_lists_tag(self, item, tag, yesno):
  self.response = self.client.get(reverse('show_item_detail', args=[item.id]))
  if yesno:
    self.has_row('tagtable', { "name": tag.name })
  else:
    self.no_row('tagtable', { "name": tag.name })

def tag_lists_item(self, tag, item, yesno):
  self.response = self.client.get(reverse('show_tag_detail', args=[tag.id]))
  if yesno:
    self.has_row('ittable', { "title": item.title })
  else:
    self.no_row('ittable', { "title": item.title })

def person_lists_tags(self, person, taglist):
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

def room_lists_item(self, room, item, yesno):
  self.response = self.client.get(reverse('show_room_detail', args=[room.id]))
  self.status_okay()
  if yesno:
    self.has_row('ritable', { "title": item.title })
  else:
    self.no_row('ritable', { "title": item.title })

def room_lists_thing(self, room, thing, yesno):
  self.response = self.client.get(reverse('show_room_detail', args=[room.id]))
  self.status_okay()
  if yesno:
    self.has_row('kratable', { "thing": thing.name })
  else:
    self.no_row('kratable', { "thing": thing.name })

def check_lists_item(self, checkname, item, yesno):
  def check_label(idx, name):
    # Model formsets use form-N-fieldname to label the fields in a form ('form' may be
    # changed by prefx). N increases linearly from 0 through the formset, while
    # form-N-id is a hidden field that contains the id of the model object.
    return "form-%d-%s" % (idx, name)
  def new_form_content(self, checkname):
    # We're completely recreating the contents of the formset, by iterating over
    # all the checks in the same order (name), and providing form-N-id and form-N-enable
    # fields, where N goes from 0 to num_checks-1.
    num_checks = Check.objects.count()
    new_form = {
      'form-TOTAL_FORMS': num_checks,
      'form-INITIAL_FORMS': num_checks,
      'form-MAX_NUM_FORMS': num_checks,
    }

    N = 0
    for check in Check.objects.order_by('name'):
      new_form[check_label(N, 'id')] = check.id
      new_form[check_label(N, 'enable')] = 1 if check.name == checkname else 0
      N = N + 1
    return new_form
  num_checks = Check.objects.count()
  checkurl = reverse('list_checks')
  self.response = self.client.get(checkurl)
  self.status_okay()
  self.response = self.client.post(checkurl, new_form_content(self, checkname) , follow=True)
  self.status_okay()
  self.form_okay()
  if yesno:
    self.has_link_to('show_item_detail', args=[item.id])
  else:
    self.no_link_to('show_item_detail', args=[item.id])
