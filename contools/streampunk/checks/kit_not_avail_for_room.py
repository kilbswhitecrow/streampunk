# This file is part of Streampunk, a Django application for convention programmes
# Copyright (C) 2014 Stephen Kilbane
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
from ..models import Room, KitThing, KitRoomAssignment

def run_check(check):
  """
  List of KitThings which are not available for rooms to which they've been assigned.
  """
  things = []

  # Only interested in scheduled items
  for kra in KitRoomAssignment.objects.all():
    if not kra.thing.available_for(kra) or not kra.room.available_for(kra):
      things.append((kra.room, kra.thing))
  return CheckOutput(check, things)
