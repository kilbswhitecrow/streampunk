# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2012 Stephen Kilbane
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
from progdb2.checks.base import CheckOutput
from progdb2.models import Item, Room

def run_check(check):
  # We want the items that overlap (a.start <= b.end and b.start <= a.end)
  # and which have the same room assigned to them.
  # Result is interesting, because we really want to return an item/room pair here,
  # not just an item.

  things = []

  # Only interested in scheduled items (that eliminates Nowhere) that are in
  # rooms that participate in clashes.
  rooms = Room.objects.filter(CanClash=True)
  for r in rooms:
    items = Item.scheduled.filter(room=r)
    for itemx in items:
      for itemy in items:
        if itemx.overlaps(itemy):
          things.append((itemx, itemy, r))
  return CheckOutput(check, things)
