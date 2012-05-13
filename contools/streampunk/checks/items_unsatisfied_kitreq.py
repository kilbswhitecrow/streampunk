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
  """
  To find the items with unsatisfied kit requests, we need to find the items that:
  - have kit requests
  - but do not have kit-thing-item-assignments that satisfy the request
  - and are not in rooms that have kit-thing-room-assignments that satisfy the request
  """
  problem_items = []
  items = Item.scheduled.annotate(num_reqs=Count('kitRequests')).exclude(num_reqs=0)
  for item in items:
    if not (item.satisfies_kit_requests() or item.room_satisfies_kit_requests()):
      problem_items.append(item)
  return CheckOutput(check, problem_items)