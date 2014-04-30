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
from ..models import Item, KitThing, KitItemAssignment, ConInfoBool

def run_check(check):
  """
  List of KitThings which are not available for items to which they've been scheduled.
  """
  things = []

  # Only interested in scheduled items
  items = Item.scheduled.all()
  for item in items:
    for kt in item.kit.all():
      if not kt.available_for(item):
        things.append((item, kt))
  return CheckOutput(check, things)
