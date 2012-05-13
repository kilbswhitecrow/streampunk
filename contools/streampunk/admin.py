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

from django.contrib import admin
from streampunk.models import SlotLength, Slot, Grid, ConDay, ItemKind, SeatingKind, PersonStatus, PersonRole
from streampunk.models import RoomCapacity, Room, Revision, Tag, ItemPerson, Item, Person, Gender, CheckResult, Check
from streampunk.models import FrontLayoutKind, KitKind, KitRole, KitDepartment, KitSource, KitBasis, KitStatus
from streampunk.models import MediaStatus, KitRequest, KitThing, KitBundle, KitRoomAssignment, KitItemAssignment
from streampunk.models import Availability, KitAvailability, RoomAvailability, PersonAvailability, PersonList
from streampunk.models import ConInfoInt, ConInfoString, ConInfoBool, UserProfile

admin.site.register(SlotLength)
admin.site.register(Slot)
admin.site.register(Grid)
admin.site.register(ConDay)
admin.site.register(ItemKind)
admin.site.register(SeatingKind)
admin.site.register(PersonStatus)
admin.site.register(PersonRole)
admin.site.register(Gender)
admin.site.register(Room)
admin.site.register(Revision)
admin.site.register(Tag)
admin.site.register(ItemPerson)
admin.site.register(Item)
admin.site.register(Person)
admin.site.register(RoomCapacity)
admin.site.register(CheckResult)
admin.site.register(Check)
admin.site.register(FrontLayoutKind)
admin.site.register(KitKind)
admin.site.register(KitRole)
admin.site.register(KitDepartment)
admin.site.register(KitSource)
admin.site.register(KitBasis)
admin.site.register(KitStatus)
admin.site.register(MediaStatus)
admin.site.register(KitRequest)
admin.site.register(KitThing)
admin.site.register(KitBundle)
admin.site.register(KitRoomAssignment)
admin.site.register(KitItemAssignment)
admin.site.register(KitAvailability)
admin.site.register(RoomAvailability)
admin.site.register(PersonAvailability)
admin.site.register(Availability)
admin.site.register(ConInfoInt)
admin.site.register(ConInfoString)
admin.site.register(ConInfoBool)
admin.site.register(PersonList)
admin.site.register(UserProfile)
