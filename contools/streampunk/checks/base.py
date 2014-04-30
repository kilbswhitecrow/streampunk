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

from ..models import Check, CheckResult
from ..models import Person, Item

class CheckOutput:
  def __init__(self, check, things):
    self.check = check
    self.things = things
    self.count = len(things)
    self.template = "streampunk/checks/%s.html" % (check.module,)
    self.person_list = check.result.name == 'Person List'
    self.item_list = check.result.name == 'Item List'
    self.mixed_tuple_list = check.result.name == 'Mixed Tuple'
    self.room_list = check.result.name == 'Room List'
    self.kitthing_list = check.result.name == 'KitThing List'

