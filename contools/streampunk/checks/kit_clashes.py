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
from progdb2.models import Item, KitItemAssignment, KitRoomAssignment, Room

def run_check(check):
  # We want the items that overlap (a.start <= b.end and b.start <= a.end)
  # and which have the same item assigned to them.
  # Also want items with kit assigned to them which overlaps with when same kit is
  # assigned to a room (which is not the room the item's in).
  # Also rooms where the same item is assigned concurrently.

  things = []

  kititems = KitItemAssignment.objects.all()
  kitrooms = KitRoomAssignment.objects.all()

  # Look for the same kithing assigned to overlapping items

  for kasx in kititems:
    for kasy in kititems:
      if not (kasx == kasy) and (kasx.thing == kasy.thing):
        if kasx.item.overlaps(kasy.item):
          things.append((kasx, kasy))

  # Look for rooms that have concurrent assignments

  for krax in kitrooms:
    for kray in kitrooms:
      if not (krax == kray) and (krax.thing == kray.thing):
        if krax.overlaps_room_assignment(kray):
          things.append((krax, kray))

  # Look for the same kit thing assigned to a room and item concurrently

  for kra in kitrooms:
    for kas in kititems:
      if kra.thing == kas.thing and not (kas.item.room == kra.room):
        if kra.overlaps(kas.item):
          things.append((kra, kas))

  # First part: Only interested in scheduled items that actually have kit things assigned
  return CheckOutput(check, things)
