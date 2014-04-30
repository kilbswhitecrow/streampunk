# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2012-2014 Stephen Kilbane
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

from django.db.models import Count
from .base import CheckOutput
from ..models import Item, ItemPerson, Person

def run_check(check):
  # We want the items that overlap (a.start <= b.end and b.start <= a.end)
  # and which have the same person assigned to them.
  # Result is interesting, because we really want to return an item/person pair here,
  # not just an item.

  things = []

  # Only interested in scheduled items that actually have people on them.
  items = Item.scheduled.all().annotate(num_people=Count('people')).filter(num_people__gt=0)
  for itemx in items:
    peoplex = itemx.people.all()
    for person in peoplex:
      # fetch the other items that person is on.
      person_items = ItemPerson.objects.filter(person=person).exclude(item=itemx)
      for pi in person_items:
        itemy = pi.item
        if itemx.overlaps(itemy):
          things.append((itemx, itemy, person))
  return CheckOutput(check, things)
