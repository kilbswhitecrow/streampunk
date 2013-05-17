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

from django.core.urlresolvers import reverse

from streampunk.models import PersonRole, PersonStatus
from streampunk.models import Slot, SlotLength, Room, ItemKind, SeatingKind
from streampunk.models import FrontLayoutKind, Revision, MediaStatus
from streampunk.models import Gender, KitKind, KitRole, KitSource, KitDepartment
from streampunk.models import KitBasis, KitStatus

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
    "coordinator": "Bob"
  }
  return def_extras(kt, extras)


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
    self.has_row('kiatable', { "name": thing.name, "kind": thing.kind, "count": thing.count })
  else:
    self.no_row('kiatable', { "name": thing.name, "kind": thing.kind, "count": thing.count })

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
    self.has_row('kiatable', { "name": thing.name, "kind": thing.kind, "count": thing.count })
  else:
    self.no_row('kiatable', { "name": thing.name, "kind": thing.kind, "count": thing.count })

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

